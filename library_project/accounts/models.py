from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile model to store additional user information
    and link Django User with library database models.
    """
    ROLES = (
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Administrator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLES, default='customer')
    is_active_employee = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_employee(self):
        return self.role == 'employee' and self.is_active_employee
    
    @property
    def is_admin(self):
        return self.role == 'admin' and self.is_active_employee

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a user is created"""
    if created:
        # Create the profile
        UserProfile.objects.create(user=instance)
        
        # Add to appropriate group based on is_staff
        if instance.is_staff:
            group, _ = Group.objects.get_or_create(name='Employees')
            instance.groups.add(group)
            
            # Set as employee
            instance.profile.role = 'employee'
            instance.profile.is_active_employee = True
            instance.profile.save()
        else:
            group, _ = Group.objects.get_or_create(name='Customers')
            instance.groups.add(group)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()