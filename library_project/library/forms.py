from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from .models import (
    Book, Author, Customer, Event, Exhibition, 
    Seminar, Rental, BookCopy, StudyRoom, Reservation,
    Topic
)

class DateTimePickerInput(forms.DateTimeInput):
    """Custom widget for datetime pickers"""
    input_type = 'datetime-local'

class BookForm(forms.ModelForm):
    """Form for creating and updating books"""
    initial_copies = forms.IntegerField(
        min_value=1,
        initial=1,
        required=False,
        help_text="Number of copies to create (only for new books)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Book
        fields = ['book_name', 'topic', 'authors']
        widgets = {
            'book_name': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make initial_copies only appear for new books
        if self.instance.pk:
            self.fields.pop('initial_copies')

class AuthorForm(forms.ModelForm):
    """Form for creating and updating authors"""
    class Meta:
        model = Author
        fields = ['fname', 'lname', 'street', 'city', 'state', 'country', 'postal_code', 'email']
        widgets = {
            'fname': forms.TextInput(attrs={'class': 'form-control'}),
            'lname': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomerForm(forms.ModelForm):
    """Form for creating and updating customers"""
    class Meta:
        model = Customer
        fields = ['fname', 'lname', 'phone', 'email', 'id_type', 'id_no']
        widgets = {
            'fname': forms.TextInput(attrs={'class': 'form-control'}),
            'lname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Passport', 'Passport'),
                ('SSN', 'Social Security Number'),
                ('Driver License', 'Driver License')
            ]),
            'id_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RentalForm(forms.ModelForm):
    """Form for creating new rentals"""
    class Meta:
        model = Rental
        fields = ['customer', 'book_copy', 'exp_return_dt']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'book_copy': forms.Select(attrs={'class': 'form-select'}),
            'exp_return_dt': DateTimePickerInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show available book copies
        self.fields['book_copy'].queryset = BookCopy.objects.filter(status='available')
        
        # Set default return date (2 weeks from now)
        if not self.instance.pk:
            self.fields['exp_return_dt'].initial = timezone.now() + timezone.timedelta(days=14)
    
    def clean_exp_return_dt(self):
        """Validate that return date is in the future"""
        exp_return_dt = self.cleaned_data.get('exp_return_dt')
        if exp_return_dt and exp_return_dt <= timezone.now():
            raise forms.ValidationError("Expected return date must be in the future.")
        return exp_return_dt

class EventForm(forms.ModelForm):
    """Form for creating and updating events"""
    class Meta:
        model = Event
        fields = ['event_name', 'start_dt', 'end_dt', 'attd_no']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_dt': DateTimePickerInput(attrs={'class': 'form-control'}),
            'end_dt': DateTimePickerInput(attrs={'class': 'form-control'}),
            'attd_no': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        """Validate that end date is after start date"""
        cleaned_data = super().clean()
        start_dt = cleaned_data.get('start_dt')
        end_dt = cleaned_data.get('end_dt')
        
        if start_dt and end_dt and start_dt >= end_dt:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

class ExhibitionForm(forms.ModelForm):
    """Form for creating and updating exhibitions"""
    class Meta:
        model = Exhibition
        fields = ['expenses']
        widgets = {
            'expenses': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SeminarForm(forms.ModelForm):
    """Form for creating and updating seminars"""
    class Meta:
        model = Seminar
        fields = ['est_auth']
        widgets = {
            'est_auth': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ReservationForm(forms.ModelForm):
    """Form for creating study room reservations"""
    class Meta:
        model = Reservation
        fields = ['topic_desc', 'start_dt', 'end_dt', 'group_size']
        widgets = {
            'topic_desc': forms.TextInput(attrs={'class': 'form-control'}),
            'start_dt': DateTimePickerInput(attrs={'class': 'form-control'}),
            'end_dt': DateTimePickerInput(attrs={'class': 'form-control'}),
            'group_size': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        """Validate reservation details"""
        cleaned_data = super().clean()
        start_dt = cleaned_data.get('start_dt')
        end_dt = cleaned_data.get('end_dt')
        group_size = cleaned_data.get('group_size')
        
        # Start must be in the future
        if start_dt and start_dt < timezone.now():
            self.add_error('start_dt', "Reservation must start in the future.")
        
        # End must be after start
        if start_dt and end_dt and start_dt >= end_dt:
            self.add_error('end_dt', "End time must be after start time.")
        
        # Duration must be reasonable (1-8 hours)
        if start_dt and end_dt:
            duration = (end_dt - start_dt).total_seconds() / 3600  # hours
            if duration < 1:
                self.add_error('end_dt', "Reservation must be at least 1 hour.")
            elif duration > 8:
                self.add_error('end_dt', "Reservation cannot exceed 8 hours.")
        
        # Group size must be positive
        if group_size is not None and group_size < 1:
            self.add_error('group_size', "Group size must be at least 1.")
        
        return cleaned_data

class TopicForm(forms.ModelForm):
    """Form for creating and updating topics"""
    class Meta:
        model = Topic
        fields = ['topic_name']
        widgets = {
            'topic_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
