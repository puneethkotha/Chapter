from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps

def employee_required(view_func):
    """Decorator for views that require employee status"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('accounts:employee_login')
        if not request.user.groups.filter(name='Employees').exists():
            return HttpResponseForbidden("You don't have permission to access this page.")
        if not request.user.profile.is_active_employee:
            return HttpResponseForbidden("Your employee account is not active. Please contact an administrator.")
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    """Decorator for views that require customer status"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('accounts:customer_login')
        if not request.user.groups.filter(name='Customers').exists():
            messages.error(request, "You need to be a customer to access this page.")
            return redirect('library:home')
        if not hasattr(request.user, 'customer_profile'):
            messages.error(request, "You need a customer profile to access this page.")
            return redirect('library:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Decorator for views that require admin status"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('accounts:employee_login')
        if not request.user.is_superuser:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper

def author_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'author_id' not in request.session:
            messages.error(request, 'Please log in as an author to access this page.')
            return redirect('library:author_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 