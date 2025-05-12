from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User, Group
from library.models import (
    Book, Author, BookCopy, Customer, Rental, Invoice, Payment,
    Topic
)
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Creates test data for the library system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create topics
        topics = [
            Topic.objects.create(topic_name='Fiction'),
            Topic.objects.create(topic_name='Science'),
            Topic.objects.create(topic_name='History'),
            Topic.objects.create(topic_name='Technology'),
        ]

        # Create authors
        authors = [
            Author.objects.create(
                fname='John',
                lname='Smith',
                postal_code='12345'
            ),
            Author.objects.create(
                fname='Jane',
                lname='Doe',
                postal_code='23456'
            ),
            Author.objects.create(
                fname='Robert',
                lname='Johnson',
                postal_code='34567'
            ),
        ]

        # Create books
        books = []
        for i in range(10):
            book = Book.objects.create(
                book_name=f'Test Book {i+1}',
                topic=random.choice(topics),
                isbn=f'978-{random.randint(100000, 999999)}-{random.randint(100, 999)}'
            )
            book.authors.add(random.choice(authors))
            books.append(book)

        # Create book copies
        for book in books:
            for i in range(random.randint(2, 5)):
                BookCopy.objects.create(
                    book=book,
                    status='available'
                )

        # Create customers
        customers = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'customer{i+1}',
                password='testpass123',
                email=f'customer{i+1}@example.com'
            )
            customer = Customer.objects.create(
                user=user,
                fname=f'Customer{i+1}',
                lname='Test',
                email=f'customer{i+1}@example.com',
                phone=f'555-{random.randint(1000, 9999)}',
                postal_code=f'{random.randint(10000, 99999)}'
            )
            customers.append(customer)

        # Create rentals and invoices
        for customer in customers:
            # Create 2-4 rentals per customer
            for _ in range(random.randint(2, 4)):
                # Get a random available book copy
                book_copy = BookCopy.objects.filter(status='available').first()
                if not book_copy:
                    continue

                # Create rental
                borrow_date = timezone.now() - timedelta(days=random.randint(1, 30))
                exp_return_dt = borrow_date + timedelta(days=14)
                
                rental = Rental.objects.create(
                    customer=customer,
                    book_copy=book_copy,
                    borrow_date=borrow_date,
                    exp_return_dt=exp_return_dt,
                    status='Borrowed'
                )
                book_copy.status = 'unavailable'
                book_copy.save()

                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_date=borrow_date,
                    invoice_amt=random.uniform(5.0, 25.0)
                )
                rental.invoice = invoice
                rental.save()

                # Randomly create some payments
                if random.random() < 0.7:  # 70% chance of payment
                    payment = Payment.objects.create(
                        payment_date=borrow_date + timedelta(days=random.randint(1, 5)),
                        pay_method=random.choice(['Credit', 'Debit', 'Cash']),
                        payment_amt=invoice.invoice_amt,
                        invoice=invoice
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 