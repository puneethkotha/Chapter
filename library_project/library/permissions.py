from rest_framework import permissions

class IsEmployee(permissions.BasePermission):
    """
    Custom permission to only allow employees to perform certain actions.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and is an employee
        return request.user.is_authenticated and request.user.groups.filter(name='Employees').exists()

class IsCustomerOrEmployee(permissions.BasePermission):
    """
    Custom permission to allow customers to view their own data and employees to view all data.
    """
    def has_object_permission(self, request, view, obj):
        # Employees can do anything
        if request.user.groups.filter(name='Employees').exists():
            return True

        # Customers can only view their own data
        if hasattr(obj, 'customer'):
            return obj.customer.user == request.user
        elif hasattr(obj, 'cust_id'):
            return obj.cust_id == request.user.customer_profile.cust_id
        return False

class IsCustomerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow customers to create their own rentals but only view others.
    """
    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow customers to create their own rentals
        return request.user.is_authenticated and request.user.groups.filter(name='Customers').exists() 