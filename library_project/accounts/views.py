from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User, Group
from .forms import (
    CustomerRegistrationForm, EmployeeRegistrationForm,
    UserLoginForm, ProfileUpdateForm
)
from .models import UserProfile

def customer_login(request):
    """Handle customer login"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is a customer
                if user.groups.filter(name='Customers').exists():
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
                    return redirect('library:home')
                else:
                    messages.error(request, "This login is for customers only. Please use the employee login if you are an employee.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/customer_login.html', {'form': form})

def employee_login(request):
    """Handle employee login"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is an employee
                if user.groups.filter(name='Employees').exists():
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
                    return redirect('library:dashboard')
                else:
                    messages.error(request, "This login is for employees only. Please use the customer login if you are a customer.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/employee_login.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('library:home')

@transaction.atomic
def register_customer(request):
    """Handle customer registration"""
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('library:home')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Add to Customer group
                customer_group = Group.objects.get(name='Customers')
                user.groups.add(customer_group)
                
                login(request, user)
                messages.success(request, f"Account created successfully! Welcome, {user.username}!")
                return redirect('library:home')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'customer'})

@login_required
@transaction.atomic
def register_employee(request):
    """Handle employee registration (admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('library:home')
    
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Add to Employee group
                employee_group = Group.objects.get(name='Employees')
                user.groups.add(employee_group)
                
                messages.success(request, f"Employee account for {user.username} created successfully!")
                return redirect('accounts:employee_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'employee'})

@login_required
def profile(request):
    """Display and update user profile"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            
            # Update customer record if exists
            if hasattr(request.user, 'customer_profile'):
                customer = request.user.customer_profile
                customer.fname = form.cleaned_data['first_name']
                customer.lname = form.cleaned_data['last_name']
                customer.email = form.cleaned_data['email']
                customer.save()
            
            messages.success(request, "Your profile has been updated!")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'is_customer': hasattr(request.user, 'customer_profile'),
        'is_employee': request.user.is_staff,
    }
    
    # Add customer info if available
    if hasattr(request.user, 'customer_profile'):
        context['customer'] = request.user.customer_profile
    
    return render(request, 'accounts/profile.html', context)

@login_required
def employee_list(request):
    """Display list of employees (admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('library:home')
    
    employees = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    
    return render(request, 'accounts/employee_list.html', {'employees': employees})

@login_required
def toggle_employee_status(request, user_id):
    """Enable/disable employee access (admin only)"""
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('library:home')
    
    try:
        employee = User.objects.get(id=user_id, is_staff=True)
        profile = employee.profile
        profile.is_active_employee = not profile.is_active_employee
        profile.save()
        
        status = "activated" if profile.is_active_employee else "deactivated"
        messages.success(request, f"Employee account for {employee.username} {status} successfully.")
    except User.DoesNotExist:
        messages.error(request, "Employee not found.")
    
    return redirect('accounts:employee_list')
