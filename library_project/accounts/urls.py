from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('customer/login/', views.customer_login, name='customer_login'),
    path('employee/login/', views.employee_login, name='employee_login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_customer, name='register'),
    path('register/employee/', views.register_employee, name='register_employee'),
    path('profile/', views.profile, name='profile'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:user_id>/toggle/', views.toggle_employee_status, name='toggle_employee_status'),
]
