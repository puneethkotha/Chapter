from django.contrib import admin
from .models import (
    Topic, Author, Book, BookAuthor, BookCopy, Customer,
    Event, Exhibition, ExhibitionAttendance, Seminar, SeminarAttendance,
    Sponsor, Individual, Organization, SeminarSponsor,
    StudyRoom, Reservation, Invoice, Payment, Rental
)

# Register your models here
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_id', 'topic_name')
    search_fields = ('topic_name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'fname', 'lname', 'email', 'country')
    list_filter = ('country',)
    search_fields = ('fname', 'lname', 'email')

class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_name', 'topic', 'available_copies_count')
    list_filter = ('topic',)
    search_fields = ('book_name',)
    inlines = [BookAuthorInline, BookCopyInline]

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('copy_id', 'book', 'status')
    list_filter = ('status',)
    search_fields = ('book__book_name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('cust_id', 'fname', 'lname', 'email', 'phone', 'id_type')
    list_filter = ('id_type',)
    search_fields = ('fname', 'lname', 'email', 'phone')

class ExhibitionInline(admin.StackedInline):
    model = Exhibition
    can_delete = False

class SeminarInline(admin.StackedInline):
    model = Seminar
    can_delete = False

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_name', 'event_type', 'start_dt', 'end_dt', 'attd_no')
    list_filter = ('event_type', 'start_dt')
    search_fields = ('event_name',)
    date_hierarchy = 'start_dt'
    
    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.event_type == 'E':
            return [ExhibitionInline]
        elif obj.event_type == 'S':
            return [SeminarInline]
        return []

@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('event', 'expenses')
    search_fields = ('event__event_name',)

@admin.register(ExhibitionAttendance)
class ExhibitionAttendanceAdmin(admin.ModelAdmin):
    list_display = ('reg_id', 'exhibition', 'customer')
    list_filter = ('exhibition',)
    search_fields = ('customer__fname', 'customer__lname', 'exhibition__event__event_name')

@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('event', 'est_auth')
    search_fields = ('event__event_name',)

@admin.register(SeminarAttendance)
class SeminarAttendanceAdmin(admin.ModelAdmin):
    list_display = ('invitation_id', 'seminar', 'author')
    list_filter = ('seminar',)
    search_fields = ('author__fname', 'author__lname', 'seminar__event__event_name')

class IndividualInline(admin.StackedInline):
    model = Individual
    can_delete = False

class OrganizationInline(admin.StackedInline):
    model = Organization
    can_delete = False

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('sponsor_id', 'sponsor_type', 'get_sponsor_name')
    list_filter = ('sponsor_type',)
    
    def get_sponsor_name(self, obj):
        if obj.sponsor_type == 'I':
            try:
                individual = Individual.objects.get(sponsor_id=obj.sponsor_id)
                return f"{individual.fname} {individual.lname}"
            except Individual.DoesNotExist:
                return "Unknown Individual"
        elif obj.sponsor_type == 'O':
            try:
                organization = Organization.objects.get(sponsor_id=obj.sponsor_id)
                return organization.org_name
            except Organization.DoesNotExist:
                return "Unknown Organization"
        return "Unknown"
    
    get_sponsor_name.short_description = 'Name'
    
    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.sponsor_type == 'I':
            return [IndividualInline]
        elif obj.sponsor_type == 'O':
            return [OrganizationInline]
        return []

@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = ('sponsor', 'fname', 'lname')
    search_fields = ('fname', 'lname')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('sponsor', 'org_name')
    search_fields = ('org_name',)

@admin.register(SeminarSponsor)
class SeminarSponsorAdmin(admin.ModelAdmin):
    list_display = ('seminar', 'sponsor', 'amount')
    list_filter = ('seminar',)

@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'capacity')
    list_filter = ('capacity',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reserve_id', 'study_room', 'customer', 'topic_desc', 'start_dt', 'end_dt', 'group_size')
    list_filter = ('study_room', 'start_dt')
    search_fields = ('topic_desc', 'customer__fname', 'customer__lname')
    date_hierarchy = 'start_dt'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'invoice_date', 'invoice_amt', 'is_paid')
    list_filter = ('invoice_date',)
    search_fields = ('invoice_id',)
    date_hierarchy = 'invoice_date'
    
    def is_paid(self, obj):
        return obj.is_paid
    
    is_paid.boolean = True
    is_paid.short_description = 'Paid'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'invoice', 'payment_date', 'pay_method', 'payment_amt')
    list_filter = ('payment_date', 'pay_method')
    search_fields = ('invoice__invoice_id', 'cardholder_name')
    date_hierarchy = 'payment_date'

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('rental_id', 'customer', 'book_copy', 'status', 'borrow_date', 'exp_return_dt', 'actual_return_dt', 'is_overdue')
    list_filter = ('status', 'borrow_date')
    search_fields = ('customer__fname', 'customer__lname', 'book_copy__book__book_name')
    date_hierarchy = 'borrow_date'
    
    def is_overdue(self, obj):
        return obj.is_overdue
    
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
