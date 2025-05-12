from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from library.models import Customer

class UserLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            }
        )
    )

class CustomerRegistrationForm(UserCreationForm):
    """
    Registration form for customer users.
    Creates both a Django User and a Customer record.
    """
    # User model fields
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Customer model fields
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    id_type = forms.ChoiceField(
        choices=[
            ('Passport', 'Passport'),
            ('SSN', 'Social Security Number'),
            ('Driver License', 'Driver License')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    id_no = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Password fields inherit from UserCreationForm but need styling
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Validate that the email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_phone(self):
        """Validate that the phone number is unique"""
        phone = self.cleaned_data.get('phone')
        if Customer.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone
    
    def clean_id_no(self):
        """Validate that the ID number is unique"""
        id_no = self.cleaned_data.get('id_no')
        id_type = self.cleaned_data.get('id_type')
        
        if Customer.objects.filter(id_no=id_no, id_type=id_type).exists():
            raise forms.ValidationError(f'This {id_type} number is already registered.')
        return id_no
    
    def save(self, commit=True):
        """Save both User and Customer objects"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Get the next available customer ID
            try:
                max_id = Customer.objects.order_by('-cust_id').first().cust_id
            except AttributeError:
                max_id = 0
            
            # Create customer record
            customer = Customer.objects.create(
                cust_id=max_id + 1,
                fname=self.cleaned_data['first_name'],
                lname=self.cleaned_data['last_name'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                id_type=self.cleaned_data['id_type'],
                id_no=self.cleaned_data['id_no'],
                address=self.cleaned_data['address'],
                user=user
            )
            
            # Link user back to customer
            from django.db import connection
            with connection.cursor() as cursor:
                user.customer_profile = customer
        
        return user

class EmployeeRegistrationForm(UserCreationForm):
    """
    Registration form for employee users.
    Creates a Django User and sets the appropriate role.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Password fields inherit from UserCreationForm but need styling
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Validate that the email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        """Save User with staff status"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        
        if commit:
            user.save()
            
            # Set profile as employee
            user.profile.role = 'employee'
            user.profile.is_active_employee = True
            user.profile.save()
        
        return user

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
