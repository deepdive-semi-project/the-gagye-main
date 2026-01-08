from urllib import request
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import mysql.connector
from decimal import Decimal
import datetime
from dateutil.relativedelta import relativedelta

from main.settings import DATABASE_HOST, DATABASE_NAME, DATABASE_PASSWORD, DATABASE_USER

def index(request):

    return render(request, "home/index.html", {})

def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

@csrf_exempt
def getExpenseDataByMonth(request):
    try:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        year = body_data.get('year')
        month = body_data.get('month')

        start_date = datetime.date(year=year, month=month, day=1)
        end_date = datetime.date(year=year, month=month, day=1) + relativedelta(months=1)

        sql = '''SELECT DATE_FORMAT(transaction_date, '%Y%m%d') as date, sum(amount) as amount, type
FROM Transactions 
WHERE transaction_date >= '{start_date} 00:00:00'
and transaction_date < '{end_date} 00:00:00'
group by date, type
'''
        sql = sql.format(start_date=start_date, end_date=end_date)
        results = executeDbQuery(sql)
        json_data = json.dumps(results, default=decimal_serializer)

        return JsonResponse({"status": "success", 
                             "year": year, 
                             "month": month,
                             "data": json_data
                             })
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def getExpenseDataByDay(request):    
    try:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        year = body_data.get('year')
        month = body_data.get('month')
        day = body_data.get('day')

        start_date = datetime.date(year=year, month=month, day=day)
        end_date = start_date + relativedelta(days=1)

        sql = '''SELECT DATE_FORMAT(transaction_date, '%Y%m%d') as date, amount, type, merchant_name
FROM Transactions 
WHERE transaction_date >= '{start_date} 00:00:00'
and transaction_date < '{end_date} 00:00:00'
'''
        sql = sql.format(start_date=start_date, end_date=end_date)
        results = executeDbQuery(sql)
        json_data = json.dumps(results, default=decimal_serializer, ensure_ascii=False)

        return JsonResponse({"status": "success", 
                             "year": year, 
                             "month": month,
                             "day": day,
                             "data": json_data
                             })
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# DB에서 데이터 불러오기
def executeDbQuery(query):
        conn = mysql.connector.connect(
            host=DATABASE_HOST,      # MySQL 서버 주소 (로컬이면 'localhost' 또는 '127.0.0.1')
            user=DATABASE_USER,           # MySQL 사용자 이름
            password=DATABASE_PASSWORD,   # MySQL 비밀번호
            database=DATABASE_NAME    # 접속할 데이터베이스 이름
        )

        # 2. 커서 객체 생성 (SQL 명령을 실행하는 도구)
        cursor = conn.cursor(dictionary=True)

        # 3. SQL 쿼리 실행 (예: SELECT 문)
        cursor.execute(query)

        # 4. 결과 가져오기
        results = cursor.fetchall()

        # 5. 변경사항 커밋 (INSERT, UPDATE, DELETE 시 필수)
        # conn.commit()

        # 6. 연결 종료 (리소스 해제)
        cursor.close()
        conn.close()

        return results