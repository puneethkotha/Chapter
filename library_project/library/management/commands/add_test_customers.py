from django.core.management.base import BaseCommand
from library.models import Customer

class Command(BaseCommand):
    help = 'Adds test customers to the database'

    def handle(self, *args, **options):
        # Get the next available customer ID
        try:
            max_id = Customer.objects.order_by('-cust_id').first().cust_id
        except AttributeError:
            max_id = 0

        # Create 100 test customers
        for i in range(1, 101):
            customer_id = max_id + i
            Customer.objects.create(
                cust_id=customer_id,
                fname=f'Test{i}',
                lname=f'Customer{i}',
                email=f'test{i}@example.com',
                phone=f'555-{i:04d}',
                id_type='Passport',
                id_no=f'PASS{i:04d}',
                address=f'{i} Test Street, Test City, TS {i:05d}, Test Country'
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created 100 test customers')) 