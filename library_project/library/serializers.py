from rest_framework import serializers
from .models import (
    Book, Author, Topic, BookCopy, Customer, Rental,
    Event, Exhibition, Seminar, StudyRoom, Reservation,
    Invoice, Payment
)

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['topic_id', 'topic_name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['author_id', 'fname', 'lname', 'email', 'city', 'country']

class BookSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    available_copies = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['book_id', 'book_name', 'topic', 'authors', 'available_copies']

    def get_available_copies(self, obj):
        return obj.available_copies_count()

class BookCopySerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = BookCopy
        fields = ['copy_id', 'status', 'book']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['cust_id', 'fname', 'lname', 'email', 'phone']

class RentalSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    book_copy = BookCopySerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Rental
        fields = [
            'rental_id', 'status', 'borrow_date', 'exp_return_dt',
            'actual_return_dt', 'customer', 'book_copy',
            'is_overdue', 'days_overdue'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue

    def get_days_overdue(self, obj):
        return obj.days_overdue()

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'event_id', 'event_name', 'start_dt', 'end_dt',
            'attd_no', 'event_type'
        ]

class ExhibitionSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Exhibition
        fields = ['event', 'expenses']

class SeminarSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Seminar
        fields = ['event', 'est_auth']

class StudyRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyRoom
        fields = ['room_id', 'capacity']

class ReservationSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    study_room = StudyRoomSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'reserve_id', 'topic_desc', 'start_dt', 'end_dt',
            'group_size', 'customer', 'study_room'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    is_paid = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'invoice_date', 'invoice_amt', 'is_paid']

    def get_is_paid(self, obj):
        return obj.is_paid

class PaymentSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'payment_date', 'pay_method',
            'cardholder_name', 'payment_amt', 'invoice'
        ] 