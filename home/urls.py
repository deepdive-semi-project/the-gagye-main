from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/expenseDataByMonth", views.getExpenseDataByMonth, name="getExpenseDataByMonth"),
    path("api/expenseDataByDay", views.getExpenseDataByDay, name="getExpenseDataByDay")
]