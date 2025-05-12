import os
import traceback

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')

    import django
    django.setup()

    from django.db import connections
    from library.models import Book

    # Test the database connection
    connection = connections['default']
    connection.cursor()
    print("Successfully connected to MySQL!")
    
    # Test a simple query if tables exist
    books = Book.objects.all()
    print(f"Found {len(books)} books in the database")
    
except Exception as e:
    print(f"Error: {e}")
    print("Full traceback:")
    traceback.print_exc()