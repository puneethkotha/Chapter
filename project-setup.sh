# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
# venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install required packages
pip install django
pip install mysqlclient
pip install python-decouple

# Create Django project
django-admin startproject library_project

# Navigate to project directory
cd library_project

# Create Django apps
python manage.py startapp accounts
python manage.py startapp library

# Create initial database migrations (once models are defined)
python manage.py makemigrations
python manage.py migrate

# Create superuser (when ready)
python manage.py createsuperuser

# Run development server
python manage.py runserver
