from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from library.models import Customer
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates sample customer and employee users'

    def handle(self, *args, **kwargs):
        # Create Groups if they don't exist
        customers_group, _ = Group.objects.get_or_create(name='Customers')
        employees_group, _ = Group.objects.get_or_create(name='Employees')

        # Create Customer user
        try:
            customer = User.objects.create_user(
                username='customer',
                password='Cust@2025',
                email='customer@example.com',
                first_name='Sample',
                last_name='Customer'
            )
            customer.groups.add(customers_group)
            
            # Create customer profile
            Customer.objects.create(
                user=customer,
                fname=customer.first_name,
                lname=customer.last_name,
                email=customer.email,
                phone='1234567890'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created customer user'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Customer user already exists or error: {str(e)}'))

        # Create Employee user
        try:
            employee = User.objects.create_user(
                username='employee',
                password='Emp@2025',
                email='employee@example.com',
                first_name='Sample',
                last_name='Employee',
                is_staff=True
            )
            employee.groups.add(employees_group)
            
            # Create employee profile
            profile = UserProfile.objects.get(user=employee)
            profile.is_active_employee = True
            profile.save()
            
            self.stdout.write(self.style.SUCCESS('Successfully created employee user'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Employee user already exists or error: {str(e)}')) 