from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Home and Dashboard
    path('', views.home, name='home'),
    path('management/', views.library_management_dashboard, name='dashboard'),
    
    # Author Authentication
    path('author/login/', views.author_login, name='author_login'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:book_id>/update/', views.book_update, name='book_update'),
    path('books/<int:book_id>/add-copies/', views.book_add_copies, name='book_add_copies'),
    path('books/search/', views.book_search, name='book_search'),
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    
    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:author_id>/', views.author_detail, name='author_detail'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/<int:author_id>/update/', views.author_update, name='author_update'),
    path('authors/seminar-registration/', views.author_seminar_registration, name='author_seminar_registration'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:cust_id>/', views.customer_detail, name='customer_detail'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:cust_id>/update/', views.customer_update, name='customer_update'),
    
    # Rentals
    path('rentals/', views.rental_list, name='rental_list'),
    path('rentals/employee/', views.employee_rental_list, name='employee_rental_list'),
    path('rentals/<int:rental_id>/', views.rental_detail, name='rental_detail'),
    path('rentals/create/', views.rental_create, name='rental_create'),
    path('rentals/<int:rental_id>/return/', views.rental_return, name='rental_return'),
    path('rentals/<int:rental_id>/mark-lost/', views.rental_mark_lost, name='rental_mark_lost'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/update/', views.event_update, name='event_update'),
    path('events/<int:event_id>/register/', views.register_exhibition, name='register_exhibition'),
    path('events/<int:event_id>/unregister/', views.unregister_exhibition, name='unregister_exhibition'),
    
    # Study Rooms
    path('rooms/', views.study_room_list, name='study_room_list'),
    path('rooms/<int:room_id>/reserve/', views.reserve_room, name='reserve_room'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:reserve_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('rooms/bookings/', views.study_room_bookings, name='study_room_bookings'),
    
    # Invoices and Payments
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/payment/', views.process_payment, name='process_payment'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
]
