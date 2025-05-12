from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from datetime import timedelta

from .models import (
    Book, Author, BookCopy, Customer, Event, Exhibition, 
    Seminar, StudyRoom, Reservation, Rental, Invoice,
    Payment, Topic, SeminarAttendance, ExhibitionAttendance
)
from .forms import (
    BookForm, AuthorForm, CustomerForm, RentalForm, 
    ReservationForm, EventForm, ExhibitionForm, SeminarForm
)
from .serializers import (
    BookSerializer, AuthorSerializer, TopicSerializer, BookCopySerializer,
    CustomerSerializer, RentalSerializer, EventSerializer, ExhibitionSerializer,
    SeminarSerializer, StudyRoomSerializer, ReservationSerializer,
    InvoiceSerializer, PaymentSerializer
)
from .permissions import IsEmployee, IsCustomerOrEmployee, IsCustomerOrReadOnly
from .decorators import employee_required, customer_required, admin_required, author_required

# Home and Dashboard Views
def home(request):
    """Home page view - accessible to all users"""
    # Redirect employees to dashboard
    if request.user.is_authenticated and request.user.groups.filter(name='Employees').exists():
        return redirect('library:dashboard')
    
    # Get library statistics
    total_books = Book.objects.count()
    active_rentals = Rental.objects.filter(status='Borrowed').count()
    
    # Get upcoming exhibitions only
    upcoming_events = Event.objects.filter(
        start_dt__gt=timezone.now(),
        event_type='E'  # Only exhibitions
    ).order_by('start_dt')[:3]
    
    # Get available study rooms (rooms without active reservations)
    now = timezone.now()
    available_rooms = StudyRoom.objects.exclude(
        reservation__start_dt__lte=now,
        reservation__end_dt__gt=now
    ).count()
    
    # Get featured books (books with available copies)
    featured_books = Book.objects.filter(
        bookcopy__status='available'
    ).distinct()[:4]
    
    # Check if user is an author (has author_id in session)
    is_author = 'author_id' in request.session if request.user.is_authenticated else False
    
    context = {
        'total_books': total_books,
        'active_rentals': active_rentals,
        'available_rooms': available_rooms,
        'upcoming_events': upcoming_events,
        'featured_books': featured_books,
        'is_authenticated': request.user.is_authenticated,
        'is_employee': request.user.groups.filter(name='Employees').exists() if request.user.is_authenticated else False,
        'is_author': is_author,
    }
    
    return render(request, 'home.html', context)

@employee_required
def library_management_dashboard(request):
    """Library management dashboard with key metrics and activities for staff"""
    # Today's activity
    today = timezone.now().date()
    new_rentals_today = Rental.objects.filter(
        borrow_date__date=today
    ).count()
    returns_today = Rental.objects.filter(
        actual_return_dt__date=today
    ).count()
    reservations_today = Reservation.objects.filter(
        start_dt__date=today
    ).count()
    
    # Weekly activity data
    week_dates = [(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
    weekly_rentals = []
    weekly_returns = []
    weekly_labels = []
    
    for date in week_dates:
        weekly_rentals.append(
            Rental.objects.filter(borrow_date__date=date).count()
        )
        weekly_returns.append(
            Rental.objects.filter(actual_return_dt__date=date).count()
        )
        weekly_labels.append(date.strftime('%a'))
    
    # Popular books data
    popular_books = Book.objects.annotate(
        rental_count=Count('bookcopy__rental')
    ).order_by('-rental_count')[:5]
    
    popular_books_labels = [f"{book.book_name[:20]}..." if len(book.book_name) > 20 
                          else book.book_name for book in popular_books]
    popular_books_data = [book.rental_count for book in popular_books]
    
    # Monthly revenue data
    last_6_months = [(today - timezone.timedelta(days=30*i)) for i in range(5, -1, -1)]
    monthly_revenue_data = []
    monthly_revenue_labels = []
    
    for month_date in last_6_months:
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1)
            
        # Calculate monthly revenue using aggregation
        month_revenue = Invoice.objects.filter(
            invoice_date__range=[month_start, month_end]
        ).aggregate(
            total=Sum('invoice_amt')
        )['total'] or 0.0  # Use 0.0 if no invoices found
        
        monthly_revenue_data.append(float(month_revenue))
        monthly_revenue_labels.append(month_date.strftime('%b %Y'))
    
    # Overdue rentals
    overdue_rentals = Rental.objects.filter(
        status='Borrowed',
        exp_return_dt__lt=timezone.now()
    ).select_related('customer', 'book_copy', 'book_copy__book')
    
    # Revenue stats - Fixed calculations
    total_invoices = Invoice.objects.count()
    
    # Calculate total revenue by summing all invoice amounts
    total_revenue = float(sum(
        invoice.invoice_amt for invoice in Invoice.objects.all()
    ))
    
    # Calculate unpaid invoices by checking if there are any payments
    unpaid_invoices = Invoice.objects.filter(
        payment__isnull=True
    ).count()
    
    context = {
        'new_rentals_today': new_rentals_today,
        'returns_today': returns_today,
        'reservations_today': reservations_today,
        'overdue_rentals': overdue_rentals,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'unpaid_invoices': unpaid_invoices,
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_rentals': json.dumps(weekly_rentals),
        'weekly_returns': json.dumps(weekly_returns),
        'popular_books_labels': json.dumps(popular_books_labels),
        'popular_books_data': json.dumps(popular_books_data),
        'monthly_revenue_labels': json.dumps(monthly_revenue_labels),
        'monthly_revenue_data': json.dumps(monthly_revenue_data),
    }
    
    return render(request, 'library/dashboard.html', context)

# Book Views
@login_required
def book_list(request):
    """Display list of books with search functionality"""
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    books = Book.objects.all()
    
    # Apply search filter
    if search_query:
        books = books.filter(
            Q(book_name__icontains=search_query) |
            Q(authors__fname__icontains=search_query) |
            Q(authors__lname__icontains=search_query) |
            Q(topic__topic_name__icontains=search_query)
        ).distinct()
    
    # Apply category filter
    if category_id:
        books = books.filter(topic_id=category_id)
    
    # Add availability information
    books = books.annotate(
        available_copies=Count('bookcopy', filter=Q(bookcopy__status='available'))
    )
    
    # Get all categories for the filter dropdown
    categories = Topic.objects.all()
    
    # Pagination
    paginator = Paginator(books, 12)  # Show 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'categories': categories,
        'search_query': search_query,
        'is_employee': request.user.groups.filter(name='Employees').exists()
    }
    return render(request, 'library/book_list.html', context)

@login_required
def book_detail(request, book_id):
    """Display book details with availability"""
    book = get_object_or_404(Book, book_id=book_id)
    
    # Get similar books based on topic
    similar_books = Book.objects.filter(
        topic=book.topic
    ).exclude(
        book_id=book.book_id
    )[:3]
    
    # Get availability information
    available_copies = book.bookcopy_set.filter(status='available').count()
    
    # Get rental history for employees
    rental_history = None
    if request.user.groups.filter(name='Employees').exists():
        rental_history = Rental.objects.filter(
            book_copy__book=book
        ).select_related('customer').order_by('-borrow_date')[:5]
    
    context = {
        'book': book,
        'similar_books': similar_books,
        'available_copies': available_copies,
        'rental_history': rental_history,
        'is_employee': request.user.groups.filter(name='Employees').exists()
    }
    return render(request, 'library/book_detail.html', context)

def book_search(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(title__icontains=query) | \
                Book.objects.filter(author__name__icontains=query) | \
                Book.objects.filter(topic__name__icontains=query)
    else:
        books = Book.objects.none()
    return render(request, 'library/book_search.html', {'books': books, 'query': query})

@employee_required
@transaction.atomic
def book_create(request):
    """Create a new book (employee only)"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.book_name}' created successfully.")
            return redirect('library:book_detail', book_id=book.book_id)
    else:
        form = BookForm()
    
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Create'})

@employee_required
@transaction.atomic
def book_update(request, book_id):
    """Update book details (employee only)"""
    book = get_object_or_404(Book, book_id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.book_name}' updated successfully.")
            return redirect('library:book_detail', book_id=book.book_id)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'library/book_form.html', {'form': form, 'book': book, 'action': 'Update'})

@employee_required
@transaction.atomic
def book_add_copies(request, book_id):
    """Add copies of a book (employee only)"""
    book = get_object_or_404(Book, book_id=book_id)
    
    if request.method == 'POST':
        num_copies = int(request.POST.get('num_copies', 1))
        
        # Create new copies
        for _ in range(num_copies):
            try:
                max_copy_id = BookCopy.objects.order_by('-copy_id').first().copy_id
            except AttributeError:
                max_copy_id = 0
                
            BookCopy.objects.create(
                copy_id=max_copy_id + 1,
                status='available',
                book=book
            )
        
        messages.success(request, f"Added {num_copies} new copies of '{book.book_name}'.")
        return redirect('library:book_detail', book_id=book.book_id)
    
    return render(request, 'library/book_add_copies.html', {'book': book})

# Author Views
def author_list(request):
    """Display list of authors with search"""
    query = request.GET.get('q', '')
    
    authors = Author.objects.all()
    
    # Apply search filter
    if query:
        authors = authors.filter(
            Q(fname__icontains=query) |
            Q(lname__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(authors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    
    return render(request, 'library/author_list.html', context)

@author_required
def author_detail(request, author_id):
    """Display author details with their books"""
    author = get_object_or_404(Author, author_id=author_id)
    books = Book.objects.filter(authors=author)
    
    context = {
        'author': author,
        'books': books,
    }
    
    return render(request, 'library/author_detail.html', context)

@employee_required
@transaction.atomic
def author_create(request):
    """Create a new author (employee only)"""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            # Get the next available author ID
            try:
                max_id = Author.objects.order_by('-author_id').first().author_id
            except AttributeError:
                max_id = 0
                
            author = form.save(commit=False)
            author.author_id = max_id + 1
            author.save()
            
            messages.success(request, f"Author '{author.full_name}' created successfully.")
            return redirect('library:author_detail', author_id=author.author_id)
    else:
        form = AuthorForm()
    
    return render(request, 'library/author_form.html', {'form': form, 'action': 'Create'})

@employee_required
def author_update(request, author_id):
    """Update an author (employee only)"""
    author = get_object_or_404(Author, author_id=author_id)
    
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, f"Author '{author.full_name}' updated successfully.")
            return redirect('library:author_detail', author_id=author.author_id)
    else:
        form = AuthorForm(instance=author)
    
    return render(request, 'library/author_form.html', {
        'form': form,
        'author': author,
        'action': 'Update'
    })

@author_required
def author_seminar_registration(request):
    """Handle author registration for seminars"""
    if request.method == 'POST':
        # Get form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        seminar_id = request.POST.get('seminar')
        bio = request.POST.get('bio')
        expertise = request.POST.get('expertise')

        try:
            # Check if author exists
            author = Author.objects.filter(email=email).first()
            if not author:
                # Create new author
                author = Author.objects.create(
                    fname=fname,
                    lname=lname,
                    email=email,
                    street=street,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country
                )

            # Get seminar
            seminar = Seminar.objects.get(event_id=seminar_id)

            # Create seminar attendance
            SeminarAttendance.objects.create(
                author=author,
                seminar=seminar,
                bio=bio,
                expertise=expertise
            )

            messages.success(request, 'Successfully registered for the seminar!')
            return redirect('library:author_detail', author_id=author.author_id)

        except Exception as e:
            messages.error(request, f'Error registering for seminar: {str(e)}')
            return redirect('library:author_seminar_registration')

    # GET request - show form
    # Get upcoming seminars
    upcoming_seminars = Seminar.objects.select_related('event').filter(
        event__start_dt__gt=timezone.now(),
        event__event_type='S'  # Only get seminars, not exhibitions
    ).order_by('event__start_dt')

    context = {
        'seminars': upcoming_seminars,
    }
    return render(request, 'library/author_seminar_registration.html', context)

def author_login(request):
    """Handle author login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            author = Author.objects.get(email=email)
            # For now, we'll use a hardcoded password for testing
            if password == 'Author@2025':
                request.session['author_id'] = author.author_id
                messages.success(request, f'Welcome back, {author.full_name}!')
                return redirect('library:author_detail', author_id=author.author_id)
            else:
                messages.error(request, 'Invalid password.')
                return redirect('library:author_login')
        except Author.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('library:author_login')
    
    return render(request, 'library/author_login.html')

# Customer Views
@employee_required
def customer_list(request):
    """Display list of customers (employee only)"""
    query = request.GET.get('q', '')
    
    customers = Customer.objects.all()
    
    # Apply search filter
    if query:
        customers = customers.filter(
            Q(fname__icontains=query) |
            Q(lname__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    
    return render(request, 'library/customer_list.html', context)

@employee_required
def customer_detail(request, cust_id):
    """Display customer details with their rentals (employee only)"""
    customer = get_object_or_404(Customer, cust_id=cust_id)
    
    # Get customer rentals
    rentals = Rental.objects.filter(customer=customer).order_by('-borrow_date')
    
    # Get customer reservations
    reservations = Reservation.objects.filter(customer=customer).order_by('-start_dt')
    
    context = {
        'customer': customer,
        'rentals': rentals,
        'reservations': reservations,
    }
    
    return render(request, 'library/customer_detail.html', context)

@employee_required
@transaction.atomic
def customer_create(request):
    """Create a new customer (employee only)"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Get the next available customer ID
            try:
                max_id = Customer.objects.order_by('-cust_id').first().cust_id
            except AttributeError:
                max_id = 0
                
            customer = form.save(commit=False)
            customer.cust_id = max_id + 1
            customer.save()
            
            messages.success(request, f"Customer '{customer.full_name}' created successfully.")
            return redirect('library:customer_detail', cust_id=customer.cust_id)
    else:
        form = CustomerForm()
    
    return render(request, 'library/customer_form.html', {'form': form, 'action': 'Create'})

@employee_required
def customer_update(request, cust_id):
    """Update a customer (employee only)"""
    customer = get_object_or_404(Customer, cust_id=cust_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.full_name}' updated successfully.")
            return redirect('library:customer_detail', cust_id=customer.cust_id)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'library/customer_form.html', {
        'form': form,
        'customer': customer,
        'action': 'Update'
    })

# Rental Views
@customer_required
def rental_list(request):
    """Display list of user's rentals"""
    rentals = Rental.objects.filter(
        customer=request.user.customer_profile
    ).select_related('book_copy', 'book_copy__book').order_by('-borrow_date')
    
    # Filter by status if specified
    status_filter = request.GET.get('status', '')
    if status_filter:
        rentals = rentals.filter(status=status_filter)
    
    context = {
        'rentals': rentals,
        'status_filter': status_filter,
        'now': timezone.now()
    }
    return render(request, 'library/rental_list.html', context)

@employee_required
def employee_rental_list(request):
    """Display all rentals (employee only)"""
    rentals = Rental.objects.all().select_related(
        'customer', 'book_copy', 'book_copy__book'
    ).order_by('-borrow_date')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    customer_id = request.GET.get('customer', '')
    
    if status_filter:
        rentals = rentals.filter(status=status_filter)
    if customer_id:
        rentals = rentals.filter(customer_id=customer_id)
    
    # Get customers for filter dropdown
    customers = Customer.objects.all()
    
    context = {
        'rentals': rentals,
        'status_filter': status_filter,
        'customers': customers,
        'selected_customer': customer_id
    }
    return render(request, 'library/employee_rental_list.html', context)

@login_required
def rental_detail(request, rental_id):
    """Display rental details"""
    rental = get_object_or_404(Rental, rental_id=rental_id)
    
    # Check if user has permission to view this rental
    if not request.user.is_staff and (
        not hasattr(request.user, 'customer_profile') or 
        rental.customer != request.user.customer_profile
    ):
        return HttpResponseForbidden("You don't have permission to view this rental.")
    
    # Calculate days overdue if applicable
    days_overdue = 0
    if rental.status == 'Borrowed' and rental.exp_return_dt < timezone.now():
        days_overdue = (timezone.now() - rental.exp_return_dt).days
    
    context = {
        'rental': rental,
        'days_overdue': days_overdue,
        'is_overdue': days_overdue > 0
    }
    
    return render(request, 'library/rental_detail.html', context)

@employee_required
@transaction.atomic
def rental_create(request):
    """Create a new rental (employee only)"""
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            # Get the next available rental ID
            try:
                max_id = Rental.objects.order_by('-rental_id').first().rental_id
            except AttributeError:
                max_id = 0
            
            rental = form.save(commit=False)
            rental.rental_id = max_id + 1
            rental.status = 'Borrowed'
            rental.borrow_date = timezone.now()
            
            # Update book copy status
            book_copy = rental.book_copy
            book_copy.status = 'unavailable'
            book_copy.save()
            
            # Create initial rental invoice
            try:
                max_invoice_id = Invoice.objects.order_by('-invoice_id').first().invoice_id
            except AttributeError:
                max_invoice_id = 0
                
            invoice = Invoice.objects.create(
                invoice_id=max_invoice_id + 1,
                invoice_date=timezone.now(),
                invoice_amt=5.00  # Base rental fee
            )
            
            # Link invoice to rental
            rental.invoice = invoice
            rental.save()
            
            messages.success(request, "Rental created successfully.")
            return redirect('library:rental_detail', rental_id=rental.rental_id)
    else:
        form = RentalForm()
    
    return render(request, 'library/rental_form.html', {'form': form})

@employee_required
@transaction.atomic
def rental_return(request, rental_id):
    """Process book return (employee only)"""
    rental = get_object_or_404(Rental, rental_id=rental_id)
    
    if rental.status != 'Borrowed':
        messages.error(request, "This book has already been returned or marked as lost.")
        return redirect('library:rental_detail', rental_id=rental_id)
    
    if request.method == 'POST':
        # Update rental status
        rental.status = 'Returned'
        rental.actual_return_dt = timezone.now()
        
        # Update book copy status
        book_copy = rental.book_copy
        book_copy.status = 'available'
        book_copy.save()
        
        # Calculate rental fee and late fees (if applicable)
        base_fee = 5.00  # Base rental fee
        days_borrowed = (rental.actual_return_dt - rental.borrow_date).days
        late_days = max(0, (rental.actual_return_dt - rental.exp_return_dt).days)
        late_fee = late_days * 1.00  # $1 per day late
        total_fee = base_fee + late_fee
        
        # Create invoice
        try:
            max_id = Invoice.objects.order_by('-invoice_id').first().invoice_id
        except AttributeError:
            max_id = 0
            
        invoice = Invoice.objects.create(
            invoice_id=max_id + 1,
            invoice_date=timezone.now(),
            invoice_amt=total_fee
        )
        
        # Link invoice to rental
        rental.invoice = invoice
        rental.save()
        
        messages.success(
            request, 
            f"Book returned successfully. Invoice #{invoice.invoice_id} "
            f"created for ${total_fee:.2f} ({late_days} days late)."
        )
        return redirect('library:rental_detail', rental_id=rental_id)
    
    return render(request, 'library/rental_return.html', {'rental': rental})

@employee_required
@transaction.atomic
def rental_mark_lost(request, rental_id):
    """Mark rental as lost (employee only)"""
    rental = get_object_or_404(Rental, rental_id=rental_id)
    
    if rental.status != 'Borrowed':
        messages.error(request, "This rental cannot be marked as lost.")
        return redirect('library:rental_detail', rental_id=rental_id)
    
    if request.method == 'POST':
        # Update rental status
        rental.status = 'Lost'
        rental.actual_return_dt = timezone.now()
        
        # Update book copy status
        book_copy = rental.book_copy
        book_copy.status = 'lost'
        book_copy.save()
        
        # Calculate fees (replacement cost + rental fee)
        replacement_cost = 25.00  # Base replacement cost
        rental_fee = 5.00  # Base rental fee
        total_fee = replacement_cost + rental_fee
        
        # Create invoice
        try:
            max_id = Invoice.objects.order_by('-invoice_id').first().invoice_id
        except AttributeError:
            max_id = 0
            
        invoice = Invoice.objects.create(
            invoice_id=max_id + 1,
            invoice_date=timezone.now(),
            invoice_amt=total_fee
        )
        
        # Link invoice to rental
        rental.invoice = invoice
        rental.save()
        
        messages.success(
            request, 
            f"Book marked as lost. Invoice #{invoice.invoice_id} "
            f"created for ${total_fee:.2f} (includes replacement cost)."
        )
        return redirect('library:rental_detail', rental_id=rental_id)
    
    return render(request, 'library/rental_mark_lost.html', {'rental': rental})

# Event Views
def event_list(request):
    """Display list of upcoming events"""
    now = timezone.now()
    
    # Get exhibitions (available to all authenticated users)
    exhibitions = Event.objects.filter(
        event_type='E'  # Changed from 'exhibition' to 'E'
    ).order_by('-start_dt')  # Order by latest first

    # Get seminars (available only to authors)
    seminars = Event.objects.filter(
        event_type='S'  # Changed from 'seminar' to 'S'
    ).order_by('-start_dt')  # Order by latest first
    
    context = {
        'exhibitions': exhibitions,
        'seminars': seminars,
        'now': now,  # Pass current time to template
    }
    return render(request, 'library/event_list.html', context)

def event_detail(request, event_id):
    """Display event details"""
    event = get_object_or_404(Event, event_id=event_id)
    
    # Check if user is registered for this event
    is_registered = False
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        if event.event_type == 'E':
            is_registered = event.exhibition.attendees.filter(
                cust_id=request.user.customer_profile.cust_id
            ).exists()
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'now': timezone.now(),
        'is_author': 'author_id' in request.session if request.user.is_authenticated else False,
    }
    return render(request, 'library/event_detail.html', context)

@employee_required
@transaction.atomic
def event_create(request):
    """Create a new event (employee only)"""
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_type = request.POST.get('event_type')
        
        if event_type == 'E':
            detail_form = ExhibitionForm(request.POST)
        else:
            detail_form = SeminarForm(request.POST)
        
        if event_form.is_valid() and detail_form.is_valid():
            # Get the next available event ID
            try:
                max_id = Event.objects.order_by('-event_id').first().event_id
            except AttributeError:
                max_id = 0
            
            # Create event
            event = event_form.save(commit=False)
            event.event_id = max_id + 1
            event.event_type = event_type
            event.save()
            
            # Create exhibition or seminar
            detail = detail_form.save(commit=False)
            detail.event_id = event.event_id
            detail.save()
            
            messages.success(request, f"Event '{event.event_name}' created successfully.")
            return redirect('library:event_detail', event_id=event.event_id)
    else:
        event_form = EventForm()
        exhibition_form = ExhibitionForm()
        seminar_form = SeminarForm()
    
    context = {
        'event_form': event_form,
        'exhibition_form': exhibition_form,
        'seminar_form': seminar_form,
    }
    
    return render(request, 'library/event_form.html', context)

@employee_required
@transaction.atomic
def event_update(request, event_id):
    """Update an existing event (employee only)"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        
        if event.event_type == 'E':
            detail_form = ExhibitionForm(request.POST, instance=event.exhibition)
        else:
            detail_form = SeminarForm(request.POST, instance=event.seminar)
        
        if event_form.is_valid() and detail_form.is_valid():
            event = event_form.save()
            detail = detail_form.save()
            
            messages.success(request, f"Event '{event.event_name}' updated successfully.")
            return redirect('library:event_detail', event_id=event.event_id)
    else:
        event_form = EventForm(instance=event)
        
        if event.event_type == 'E':
            detail_form = ExhibitionForm(instance=event.exhibition)
            exhibition_form = detail_form
            seminar_form = SeminarForm()
        else:
            detail_form = SeminarForm(instance=event.seminar)
            seminar_form = detail_form
            exhibition_form = ExhibitionForm()
    
    context = {
        'event_form': event_form,
        'exhibition_form': exhibition_form,
        'seminar_form': seminar_form,
        'event': event,
    }
    
    return render(request, 'library/event_form.html', context)

@login_required
@transaction.atomic
def register_exhibition(request, event_id):
    """Register for an exhibition (customer only)"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if event.event_type != 'E':
        messages.error(request, "This event is not an exhibition.")
        return redirect('library:event_detail', event_id=event_id)
    
    if event.end_dt < timezone.now():
        messages.error(request, "This exhibition has already ended.")
        return redirect('library:event_detail', event_id=event_id)
    
    try:
        customer = request.user.customer_profile
    except (AttributeError, Customer.DoesNotExist):
        messages.error(request, "You need a customer profile to register for exhibitions.")
        return redirect('library:event_detail', event_id=event_id)
    
    exhibition = Exhibition.objects.get(event_id=event.event_id)
    
    # Check if already registered
    if exhibition.attendees.filter(cust_id=customer.cust_id).exists():
        messages.info(request, "You are already registered for this exhibition.")
        return redirect('library:event_detail', event_id=event_id)
    
    # Check if exhibition is full
    current_attendees = exhibition.attendees.count()
    if current_attendees >= event.attd_no:
        messages.error(request, "Sorry, this exhibition is full.")
        return redirect('library:event_detail', event_id=event_id)
    
    # Create registration
    ExhibitionAttendance.objects.create(
        exhibition=exhibition,
        customer=customer
    )
    
    messages.success(request, "Successfully registered for the exhibition!")
    return redirect('library:event_detail', event_id=event_id)

@login_required
@transaction.atomic
def unregister_exhibition(request, event_id):
    """Unregister from an exhibition (customer only)"""
    event = get_object_or_404(Event, event_id=event_id)
    
    if event.event_type != 'E':
        messages.error(request, "This event is not an exhibition.")
        return redirect('library:event_detail', event_id=event_id)
    
    # Check if user has a customer profile
    if not hasattr(request.user, 'customer_profile'):
        messages.error(request, "You need a customer profile to unregister from exhibitions.")
        return redirect('library:event_detail', event_id=event_id)
    
    customer = request.user.customer_profile
    exhibition = Exhibition.objects.get(event_id=event.event_id)
    
    # Check if registered
    attendance = ExhibitionAttendance.objects.filter(
        exhibition=exhibition,
        customer=customer
    ).first()
    
    if not attendance:
        messages.info(request, "You are not registered for this exhibition.")
        return redirect('library:event_detail', event_id=event_id)
    
    # Delete registration
    attendance.delete()
    messages.success(request, "Successfully unregistered from the exhibition.")
    return redirect('library:event_detail', event_id=event_id)

# Study Room Views
@login_required
def study_room_list(request):
    """Display list of study rooms with availability"""
    # Get all study rooms
    rooms = StudyRoom.objects.all()
    
    # Get current time for availability check
    now = timezone.now()
    
    # Check availability for each room
    for room in rooms:
        room.is_available = not Reservation.objects.filter(
            study_room=room,
            start_dt__lte=now,
            end_dt__gt=now
        ).exists()
    
    context = {
        'rooms': rooms,
    }
    return render(request, 'library/study_room_list.html', context)

@login_required
@transaction.atomic
def reserve_room(request, room_id):
    """Reserve a study room (customer only)"""
    room = get_object_or_404(StudyRoom, room_id=room_id)
    
    # Check if user has a customer profile
    try:
        customer = request.user.customer_profile
    except (AttributeError, Customer.DoesNotExist):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': "You need a customer profile to reserve rooms."})
        messages.error(request, "You need a customer profile to reserve rooms.")
        return redirect('library:study_room_list')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            start_dt = form.cleaned_data['start_dt']
            end_dt = form.cleaned_data['end_dt']
            
            # Check for conflicts
            conflicts = Reservation.objects.filter(
                study_room=room,
                start_dt__lt=end_dt,
                end_dt__gt=start_dt
            )
            
            if conflicts.exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'errors': "The room is already reserved during this time. Please choose another time."
                    })
                messages.error(
                    request, 
                    "The room is already reserved during this time. Please choose another time."
                )
            else:
                # Get the next available reservation ID
                try:
                    max_id = Reservation.objects.order_by('-reserve_id').first().reserve_id
                except AttributeError:
                    max_id = 0
                
                # Create reservation
                reservation = form.save(commit=False)
                reservation.reserve_id = max_id + 1
                reservation.customer = customer
                reservation.study_room = room
                reservation.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': "Room reserved successfully.",
                        'reservation': {
                            'id': reservation.reserve_id,
                            'room_id': room.room_id,
                            'start_dt': start_dt.isoformat(),
                            'end_dt': end_dt.isoformat()
                        }
                    })
                
                messages.success(request, "Room reserved successfully.")
                return redirect('library:my_reservations')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors})
    else:
        # Initialize with default times (2 hours from now)
        now = timezone.now()
        form = ReservationForm(initial={
            'start_dt': now.replace(minute=(now.minute // 30) * 30, second=0, microsecond=0) + 
                        timezone.timedelta(hours=1),
            'end_dt': now.replace(minute=(now.minute // 30) * 30, second=0, microsecond=0) + 
                      timezone.timedelta(hours=3),
        })
    
    context = {
        'form': form,
        'room': room,
    }
    
    return render(request, 'library/reservation_form.html', context)

@login_required
def my_reservations(request):
    """View for customers to see their study room reservations"""
    if not hasattr(request.user, 'customer_profile'):
        messages.error(request, 'You must be a customer to view reservations.')
        return redirect('library:home')
    
    customer = request.user.customer_profile
    print(f"Debug - Customer ID: {customer.cust_id}")
    
    # Get all reservations for the customer
    all_reservations = Reservation.objects.filter(
        customer=customer
    ).select_related('study_room').order_by('-start_dt')
    
    print(f"Debug - Total reservations found: {all_reservations.count()}")
    
    # Split into upcoming and past reservations
    current_time = timezone.now()
    upcoming_reservations = all_reservations.filter(end_dt__gt=current_time)
    past_reservations = all_reservations.filter(end_dt__lte=current_time)
    
    print(f"Debug - Upcoming reservations: {upcoming_reservations.count()}")
    print(f"Debug - Past reservations: {past_reservations.count()}")
    
    # Print first few reservations for debugging
    for res in all_reservations[:3]:
        print(f"Debug - Reservation: ID={res.reserve_id}, Start={res.start_dt}, End={res.end_dt}")
    
    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'library/my_reservations.html', context)

@employee_required
def study_room_bookings(request):
    """Display all study room bookings for employees"""
    # Get all reservations with related data
    reservations = Reservation.objects.select_related(
        'study_room', 'customer'
    ).order_by('-start_dt')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            reservations = reservations.filter(
                start_dt__date=filter_date
            )
        except ValueError:
            messages.error(request, 'Invalid date format')
    
    # Filter by room if provided
    room_filter = request.GET.get('room')
    if room_filter:
        reservations = reservations.filter(study_room_id=room_filter)
    
    # Get all rooms for the filter dropdown
    rooms = StudyRoom.objects.all()
    
    context = {
        'reservations': reservations,
        'rooms': rooms,
        'date_filter': date_filter,
        'room_filter': room_filter,
        'now': timezone.now()  # Add current time for status comparison
    }
    return render(request, 'library/study_room_bookings.html', context)

@employee_required
def reservation_list(request):
    """Display all reservations (employee only)"""
    reservations = Reservation.objects.all().select_related(
        'customer', 'study_room'
    ).order_by('-start_dt')
    
    # Apply filters
    date_filter = request.GET.get('date', '')
    room_filter = request.GET.get('room', '')
    
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            reservations = reservations.filter(start_dt__date=filter_date)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    if room_filter:
        reservations = reservations.filter(study_room_id=room_filter)
    
    # Get rooms for filter dropdown
    rooms = StudyRoom.objects.all()
    
    context = {
        'reservations': reservations,
        'rooms': rooms,
        'date_filter': date_filter,
        'room_filter': room_filter
    }
    return render(request, 'library/reservation_list.html', context)

# Invoice and Payment Views
@login_required
def invoice_list(request):
    """Display list of invoices with filters"""
    # For customers, show only their invoices; for employees, show all
    if request.user.is_staff:
        paid_filter = request.GET.get('paid', '')
        
        invoices = Invoice.objects.all()
        
        # Apply paid filter
        if paid_filter == 'paid':
            # Find paid invoices (complex query)
            paid_invoice_ids = []
            for invoice in invoices:
                if invoice.is_paid:
                    paid_invoice_ids.append(invoice.invoice_id)
            
            invoices = invoices.filter(invoice_id__in=paid_invoice_ids)
        elif paid_filter == 'unpaid':
            # Find unpaid invoices (complex query)
            unpaid_invoice_ids = []
            for invoice in invoices:
                if not invoice.is_paid:
                    unpaid_invoice_ids.append(invoice.invoice_id)
            
            invoices = invoices.filter(invoice_id__in=unpaid_invoice_ids)
    else:
        # Try to get customer profile
        try:
            customer = request.user.customer_profile
            rental_ids = Rental.objects.filter(customer=customer).values_list('invoice_id', flat=True)
            invoices = Invoice.objects.filter(invoice_id__in=rental_ids)
            
            paid_filter = request.GET.get('paid', '')
            # Apply paid filter for customer view
            if paid_filter == 'paid':
                # Find paid invoices
                paid_invoice_ids = []
                for invoice in invoices:
                    if invoice.is_paid:
                        paid_invoice_ids.append(invoice.invoice_id)
                
                invoices = invoices.filter(invoice_id__in=paid_invoice_ids)
            elif paid_filter == 'unpaid':
                # Find unpaid invoices
                unpaid_invoice_ids = []
                for invoice in invoices:
                    if not invoice.is_paid:
                        unpaid_invoice_ids.append(invoice.invoice_id)
                
                invoices = invoices.filter(invoice_id__in=unpaid_invoice_ids)
        except (AttributeError, Customer.DoesNotExist):
            messages.error(request, "You don't have a customer profile.")
            return redirect('library:home')
    
    # Pagination
    paginator = Paginator(invoices.order_by('-invoice_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'paid_filter': paid_filter,
    }
    
    return render(request, 'library/invoice_list.html', context)

@login_required
def invoice_detail(request, invoice_id):
    """Display invoice details with payments"""
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    
    # Check if user has permission to view this invoice
    if not request.user.is_staff:
        try:
            customer = request.user.customer_profile
            rental = Rental.objects.get(invoice=invoice)
            
            if rental.customer != customer:
                return HttpResponseForbidden("You don't have permission to view this invoice.")
        except (AttributeError, Customer.DoesNotExist, Rental.DoesNotExist):
            return HttpResponseForbidden("You don't have permission to view this invoice.")
    
    # Get related rental
    try:
        rental = Rental.objects.get(invoice=invoice)
    except Rental.DoesNotExist:
        rental = None
    
    # Get payments
    payments = Payment.objects.filter(invoice=invoice)
    
    # Calculate totals
    total_paid = sum(payment.payment_amt for payment in payments)
    balance = max(0, invoice.invoice_amt - total_paid)
    
    context = {
        'invoice': invoice,
        'rental': rental,
        'payments': payments,
        'total_paid': total_paid,
        'balance': balance,
        'is_paid': invoice.is_paid,
    }
    
    return render(request, 'library/invoice_detail.html', context)

@login_required
@transaction.atomic
def process_payment(request, invoice_id):
    """Process payment for an invoice and handle rental return"""
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    
    # Get the associated rental
    try:
        rental = Rental.objects.get(invoice=invoice)
    except Rental.DoesNotExist:
        messages.error(request, "No rental found for this invoice.")
        return redirect('library:invoice_list')
    
    if request.method == 'POST':
        try:
            # Create payment for the full amount
            try:
                max_id = Payment.objects.order_by('-payment_id').first().payment_id
            except AttributeError:
                max_id = 0
            
            Payment.objects.create(
                payment_id=max_id + 1,
                payment_date=timezone.now(),
                pay_method='Cash',  # Default payment method
                payment_amt=invoice.invoice_amt,
                invoice=invoice
            )
            
            # Update rental status
            rental.status = 'Returned'
            rental.actual_return_dt = timezone.now()
            rental.save()
            
            # Update book copy status
            book_copy = rental.book_copy
            book_copy.status = 'available'
            book_copy.save()
            
            messages.success(request, "Payment processed successfully and book has been returned.")
            return redirect('library:rental_list')
            
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect('library:invoice_detail', invoice_id=invoice_id)
    
    return render(request, 'library/process_payment.html', {
        'invoice': invoice,
        'rental': rental
    })

@login_required
@transaction.atomic
def cancel_reservation(request, reserve_id):
    """Cancel a reservation (owner or employee only)"""
    reservation = get_object_or_404(Reservation, reserve_id=reserve_id)
    
    # Check permission
    is_owner = (
        hasattr(request.user, 'customer_profile') and 
        reservation.customer == request.user.customer_profile
    )
    
    if not (is_owner or request.user.is_staff):
        return HttpResponseForbidden("You don't have permission to cancel this reservation.")
    
    # Prevent cancellation of past reservations
    if reservation.start_dt < timezone.now():
        messages.error(request, "Cannot cancel a reservation that has already started.")
        if is_owner:
            return redirect('library:my_reservations')
        return redirect('library:study_room_list')
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation canceled successfully.")
        
        if is_owner:
            return redirect('library:my_reservations')
        return redirect('library:study_room_list')
    
    return render(request, 'library/cancel_reservation.html', {'reservation': reservation})

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsCustomerOrReadOnly]

    @action(detail=True, methods=['get'])
    def available_copies(self, request, pk=None):
        book = self.get_object()
        copies = book.bookcopy_set.filter(status='available')
        serializer = BookCopySerializer(copies, many=True)
        return Response(serializer.data)

class RentalViewSet(viewsets.ModelViewSet):
    serializer_class = RentalSerializer
    permission_classes = [IsCustomerOrEmployee]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Employees').exists():
            return Rental.objects.all()
        return Rental.objects.filter(customer__user=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer_profile)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsCustomerOrReadOnly]

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if event.event_type == 'E':
            attendees = event.exhibition.attendees.all()
            serializer = CustomerSerializer(attendees, many=True)
        else:
            attendees = event.seminar.authors.all()
            serializer = AuthorSerializer(attendees, many=True)
        return Response(serializer.data)

class StudyRoomViewSet(viewsets.ModelViewSet):
    queryset = StudyRoom.objects.all()
    serializer_class = StudyRoomSerializer
    permission_classes = [IsCustomerOrReadOnly]

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        room = self.get_object()
        current_time = timezone.now()
        reservations = room.reservation_set.filter(
            start_dt__lte=current_time,
            end_dt__gte=current_time
        )
        is_available = not reservations.exists()
        return Response({'is_available': is_available})

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsCustomerOrEmployee]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Employees').exists():
            return Reservation.objects.all()
        return Reservation.objects.filter(customer__user=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer_profile)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsEmployee]

    @action(detail=True, methods=['get'])
    def rentals(self, request, pk=None):
        customer = self.get_object()
        rentals = customer.rental_set.all()
        serializer = RentalSerializer(rentals, many=True)
        return Response(serializer.data)

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsCustomerOrEmployee]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Employees').exists():
            return Invoice.objects.all()
        return Invoice.objects.filter(rental__customer__user=user)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsEmployee]

    def get_queryset(self):
        return Payment.objects.all()

@login_required
def profile(request):
    return render(request, 'library/profile.html')

@customer_required
@transaction.atomic
def borrow_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    customer = request.user.customer_profile
    
    # Check if customer already has an active rental for this book
    active_rental = Rental.objects.filter(
        customer=customer,
        book_copy__book=book,
        status='Borrowed'
    ).first()
    
    if active_rental:
        messages.error(request, f'You already have an active rental for "{book.book_name}". Please return it before borrowing another copy.')
        return redirect('library:book_detail', book_id=book_id)
    
    # Get available copies
    available_copies = book.bookcopy_set.filter(status='available')
    
    if not available_copies.exists():
        messages.error(request, 'Sorry, no copies of this book are currently available.')
        return redirect('library:book_detail', book_id=book_id)
    
    if request.method == 'POST':
        try:
            # Get the first available copy
            book_copy = available_copies.first()
            
            # Create rental
            rental = Rental.objects.create(
                customer=customer,
                book_copy=book_copy,
                borrow_date=timezone.now(),
                exp_return_dt=timezone.now() + timezone.timedelta(days=14),
                status='Borrowed'
            )
            
            # Create invoice
            invoice = Invoice.objects.create(
                invoice_date=timezone.now(),
                invoice_amt=0.00  # Will be updated when book is returned
            )
            
            # Link invoice to rental
            rental.invoice = invoice
            rental.save()
            
            # Update book copy status
            book_copy.status = 'not available'
            book_copy.save()
            
            messages.success(request, f'Successfully borrowed "{book.book_name}". Please return it by {rental.exp_return_dt.strftime("%B %d, %Y")}.')
            return redirect('library:rental_list')
            
        except Exception as e:
            messages.error(request, f'Error borrowing book: {str(e)}')
            return redirect('library:book_detail', book_id=book_id)
    
    # For GET requests, show the borrow confirmation page
    return render(request, 'library/borrow_book.html', {
        'book': book,
        'available_copies': available_copies.count()
    })
