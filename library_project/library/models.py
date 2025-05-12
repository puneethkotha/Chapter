from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Topic(models.Model):
    """Maps to PJI_TOPIC table"""
    topic_id = models.BigAutoField(primary_key=True, db_column='TOPIC_ID')
    topic_name = models.CharField(max_length=50, db_column='TOPIC_NAME')
    
    class Meta:
        db_table = 'PJI_TOPIC'
        managed = True
        
    def __str__(self):
        return self.topic_name

class Author(models.Model):
    """Maps to PJI_AUTHOR table"""
    author_id = models.BigAutoField(primary_key=True, db_column='AUTHOR_ID')
    fname = models.CharField(max_length=50, db_column='FNAME')
    lname = models.CharField(max_length=50, db_column='LNAME')
    street = models.CharField(max_length=50, db_column='STREET')
    city = models.CharField(max_length=50, db_column='CITY')
    state = models.CharField(max_length=50, null=True, blank=True, db_column='STATE')
    country = models.CharField(max_length=50, db_column='COUNTRY')
    postal_code = models.CharField(max_length=20, db_column='POSTAL_CODE')
    email = models.EmailField(max_length=254, db_column='EMAIL')
    
    class Meta:
        db_table = 'PJI_AUTHOR'
        managed = True
        
    def __str__(self):
        return f"{self.fname} {self.lname}"
    
    @property
    def full_name(self):
        return f"{self.fname} {self.lname}"

class Book(models.Model):
    """Maps to PJI_BOOK table"""
    book_id = models.BigAutoField(primary_key=True, db_column='BOOK_ID')
    book_name = models.CharField(max_length=100, db_column='BOOK_NAME')
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        db_column='PJI_TOPIC_TOPIC_ID',
        null=True,
        blank=True
    )
    authors = models.ManyToManyField(Author, through='BookAuthor')
    
    class Meta:
        db_table = 'PJI_BOOK'
        managed = True
        
    def __str__(self):
        return self.book_name
    
    def available_copies_count(self):
        return self.bookcopy_set.filter(status='available').count()

class BookAuthor(models.Model):
    """Maps to PJI_BOOK_AUTHOR table"""
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        db_column='PJI_BOOK_BOOK_ID'
    )
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        db_column='PJI_AUTHOR_AUTHOR_ID'
    )
    
    class Meta:
        db_table = 'PJI_BOOK_AUTHOR'
        managed = True
        unique_together = (('book', 'author'),)

class BookCopy(models.Model):
    """Maps to PJI_BOOK_COPY table"""
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('not available', 'Not Available'),
    )
    
    copy_id = models.BigAutoField(primary_key=True, db_column='COPY_ID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_column='STATUS')
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        db_column='PJI_BOOK_BOOK_ID'
    )
    
    class Meta:
        db_table = 'PJI_BOOK_COPY'
        managed = True
        verbose_name_plural = 'Book copies'
        
    def __str__(self):
        return f"{self.book.book_name} (Copy #{self.copy_id})"

class Customer(models.Model):
    """Maps to PJI_CUSTOMER table"""
    cust_id = models.BigAutoField(primary_key=True, db_column='CUST_ID')
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='customer_profile'
    )
    fname = models.CharField(max_length=50, db_column='FNAME')
    lname = models.CharField(max_length=50, db_column='LNAME')
    phone = models.CharField(max_length=15, db_column='PHONE')
    email = models.EmailField(max_length=254, db_column='EMAIL')
    id_type = models.CharField(max_length=50, db_column='ID_TYPE')
    id_no = models.CharField(max_length=30, db_column='ID_NO')
    address = models.TextField(max_length=500, db_column='ADDRESS', null=True, blank=True)

    class Meta:
        db_table = 'PJI_CUSTOMER'
        managed = True

    def __str__(self):
        return f"{self.fname} {self.lname}"

    @property
    def full_name(self):
        return f"{self.fname} {self.lname}"

    def active_rentals(self):
        return self.rental_set.filter(status='Borrowed')

class Event(models.Model):
    """Maps to PJI_EVENT table"""
    EVENT_TYPES = (
        ('E', 'Exhibition'),
        ('S', 'Seminar'),
    )
    
    event_id = models.BigAutoField(primary_key=True, db_column='EVENT_ID')
    event_name = models.CharField(max_length=100, db_column='EVENT_NAME')
    start_dt = models.DateTimeField(db_column='START_DT')
    end_dt = models.DateTimeField(db_column='END_DT')
    attd_no = models.BigIntegerField(db_column='ATTD_NO')
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES, db_column='EVENT_TYPE')
    
    class Meta:
        db_table = 'PJI_EVENT'
        managed = True
        
    def __str__(self):
        return self.event_name
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_dt <= now <= self.end_dt

class Exhibition(models.Model):
    """Maps to PJI_EXHIBITION table"""
    event = models.OneToOneField(
        Event, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='EVENT_ID'
    )
    expenses = models.DecimalField(max_digits=10, decimal_places=2, db_column='EXPENSES')
    attendees = models.ManyToManyField(Customer, through='ExhibitionAttendance')
    
    class Meta:
        db_table = 'PJI_EXHIBITION'
        managed = True
        
    def __str__(self):
        return f"Exhibition: {self.event.event_name}"

class ExhibitionAttendance(models.Model):
    """Maps to PJI_EXH_ATTD table"""
    reg_id = models.BigAutoField(primary_key=True, db_column='REG_ID')
    exhibition = models.ForeignKey(
        Exhibition, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_EXHIBITION_EVENT_ID'
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_CUSTOMER_CUST_ID'
    )
    
    class Meta:
        db_table = 'PJI_EXH_ATTD'
        managed = True
        
    def __str__(self):
        if self.exhibition and self.customer:
            return f"{self.customer.full_name} - {self.exhibition.event.event_name}"
        return f"Registration #{self.reg_id}"

class Seminar(models.Model):
    """Maps to PJI_SEMINAR table"""
    event = models.OneToOneField(
        Event, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='EVENT_ID'
    )
    est_auth = models.IntegerField(null=True, blank=True, db_column='EST_AUTH')
    authors = models.ManyToManyField(Author, through='SeminarAttendance')
    
    class Meta:
        db_table = 'PJI_SEMINAR'
        managed = True
        
    def __str__(self):
        return f"Seminar: {self.event.event_name}"

class SeminarAttendance(models.Model):
    """Maps to PJI_SEMINAR_ATTD table"""
    invitation_id = models.BigAutoField(primary_key=True, db_column='INVITATION_ID')
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_AUTHOR_AUTHOR_ID'
    )
    seminar = models.ForeignKey(
        Seminar, 
        on_delete=models.CASCADE, 
        db_column='PJI_SEMINAR_EVENT_ID'
    )
    
    class Meta:
        db_table = 'PJI_SEMINAR_ATTD'
        managed = True
        
    def __str__(self):
        if self.author and self.seminar:
            return f"{self.author.full_name} - {self.seminar.event.event_name}"
        return f"Invitation #{self.invitation_id}"

class Sponsor(models.Model):
    """Maps to PJI_SPONSOR table"""
    SPONSOR_TYPES = (
        ('I', 'Individual'),
        ('O', 'Organization'),
    )
    
    sponsor_id = models.BigAutoField(primary_key=True, db_column='SPONSOR_ID')
    sponsor_type = models.CharField(max_length=1, choices=SPONSOR_TYPES, db_column='SPONSOR_TYPE')
    
    class Meta:
        db_table = 'PJI_SPONSOR'
        managed = True
        
    def __str__(self):
        return f"Sponsor #{self.sponsor_id}"

class Individual(models.Model):
    """Maps to PJI_INDIVIDUAL table"""
    sponsor = models.OneToOneField(
        Sponsor, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='SPONSOR_ID'
    )
    fname = models.CharField(max_length=50, db_column='FNAME')
    lname = models.CharField(max_length=50, db_column='LNAME')
    
    class Meta:
        db_table = 'PJI_INDIVIDUAL'
        managed = True
        
    def __str__(self):
        return f"{self.fname} {self.lname}"

class Organization(models.Model):
    """Maps to PJI_ORG table"""
    sponsor = models.OneToOneField(
        Sponsor, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        db_column='SPONSOR_ID'
    )
    org_name = models.CharField(max_length=50, db_column='ORG_NAME')
    
    class Meta:
        db_table = 'PJI_ORG'
        managed = True
        
    def __str__(self):
        return self.org_name

class SeminarSponsor(models.Model):
    """Maps to PJI_SEM_SPONSOR table"""
    seminar = models.ForeignKey(
        Seminar, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_SEMINAR_EVENT_ID'
    )
    sponsor = models.ForeignKey(
        Sponsor, 
        on_delete=models.CASCADE, 
        db_column='PJI_SPONSOR_SPONSOR_ID'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='AMOUNT')
    
    class Meta:
        db_table = 'PJI_SEM_SPONSOR'
        managed = True
        unique_together = (('seminar', 'sponsor'),)
        
    def __str__(self):
        if self.seminar:
            return f"{self.sponsor} - {self.seminar.event.event_name}"
        return f"Sponsorship by {self.sponsor}"

class StudyRoom(models.Model):
    """Maps to PJI_STUDY_ROOM table"""
    room_id = models.BigAutoField(primary_key=True, db_column='ROOM_ID')
    capacity = models.IntegerField(db_column='CAPACITY')
    
    class Meta:
        db_table = 'PJI_STUDY_ROOM'
        managed = True
        
    def __str__(self):
        return f"Study Room #{self.room_id} (Capacity: {self.capacity})"

class Reservation(models.Model):
    """Maps to PJI_RESERVATION table"""
    reserve_id = models.BigAutoField(primary_key=True, db_column='RESERVE_ID')
    topic_desc = models.CharField(max_length=255, db_column='TOPIC_DESC')
    start_dt = models.DateTimeField(db_column='START_DT')
    end_dt = models.DateTimeField(db_column='END_DT')
    group_size = models.IntegerField(db_column='GROUP_SIZE')
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_CUSTOMER_CUST_ID'
    )
    study_room = models.ForeignKey(
        StudyRoom, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_STUDY_ROOM_ROOM_ID'
    )
    
    class Meta:
        db_table = 'PJI_RESERVATION'
        managed = True
        
    def __str__(self):
        if self.customer and self.study_room:
            return f"{self.customer.full_name} - Room #{self.study_room.room_id}"
        return f"Reservation #{self.reserve_id}"

class Invoice(models.Model):
    """Maps to PJI_INVOICE table"""
    invoice_id = models.BigAutoField(primary_key=True, db_column='INVOICE_ID')
    invoice_date = models.DateTimeField(db_column='INVOICE_DATE')
    invoice_amt = models.DecimalField(max_digits=10, decimal_places=2, db_column='INVOICE_AMT')
    
    class Meta:
        db_table = 'PJI_INVOICE'
        managed = True
        
    def __str__(self):
        return f"Invoice #{self.invoice_id}"
    
    @property
    def is_paid(self):
        total_paid = sum(p.payment_amt for p in self.payment_set.all())
        return total_paid >= self.invoice_amt

class Payment(models.Model):
    """Maps to PJI_PAYMENT table"""
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Credit', 'Credit Card'),
        ('Debit', 'Debit Card'),
        ('PayPal', 'PayPal'),
    )
    
    payment_id = models.BigAutoField(primary_key=True, db_column='PAYMENT_ID')
    payment_date = models.DateTimeField(db_column='PAYMENT_DATE')
    pay_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, db_column='PAY_METHOD')
    cardholder_name = models.CharField(max_length=100, null=True, blank=True, db_column='CARDHOLDER_NAME')
    payment_amt = models.DecimalField(max_digits=10, decimal_places=2, db_column='PAYMENT_AMT')
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_INVOICE_INVOICE_ID'
    )
    
    class Meta:
        db_table = 'PJI_PAYMENT'
        managed = True
        
    def __str__(self):
        return f"Payment #{self.payment_id} ({self.payment_amt})"

class Rental(models.Model):
    """Maps to PJI_RENTAL table"""
    RENTAL_STATUS = (
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Late', 'Late'),
        ('Lost', 'Lost'),
    )
    
    rental_id = models.BigAutoField(primary_key=True, db_column='RENTAL_ID')
    status = models.CharField(max_length=25, choices=RENTAL_STATUS, db_column='STATUS')
    borrow_date = models.DateTimeField(db_column='BORROW_DATE')
    exp_return_dt = models.DateTimeField(db_column='EXP_RETURN_DT')
    actual_return_dt = models.DateTimeField(null=True, blank=True, db_column='ACTUAL_RETURN_DT')
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_CUSTOMER_CUST_ID'
    )
    invoice = models.OneToOneField(
        Invoice, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_INVOICE_INVOICE_ID'
    )
    book_copy = models.ForeignKey(
        BookCopy, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='PJI_BOOK_COPY_COPY_ID'
    )
    
    class Meta:
        db_table = 'PJI_RENTAL'
        managed = True
        
    def __str__(self):
        if self.customer and self.book_copy:
            return f"{self.customer.full_name} - {self.book_copy.book.book_name}"
        return f"Rental #{self.rental_id}"
    
    @property
    def is_overdue(self):
        if self.status == 'Returned':
            return False
        return timezone.now() > self.exp_return_dt
    
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        if self.status == 'Returned' and self.actual_return_dt:
            days = (self.actual_return_dt - self.exp_return_dt).days
        else:
            days = (timezone.now() - self.exp_return_dt).days
        return max(0, days)