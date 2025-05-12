# Library Management System

A comprehensive library management system built with Django that allows users to manage books, rentals, events, and study room reservations.

## Team Members
- PUNEETH KOTHA (pk3058)
- JAYRAJ MANOJ PAMNANI (jmp10051)
- ILKA JEAN (ifj2007)

## Features

- User Authentication (Customers, Employees, Authors)
- Book Management
- Rental System
- Study Room Reservations
- Event Management
- Payment Processing
- RESTful API

## Tech Stack

- Backend: Django 4.2
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript
- Database: MySQL
- API: Django REST Framework

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root and add:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost:3306/library_db
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
library_project/
├── library_project/          # Project configuration
├── library/                 # Main application
├── accounts/               # User management app
├── templates/             # HTML templates
├── static/               # Static files
└── manage.py            # Django management script
```

## API Documentation

The API endpoints are available at `/api/` and include:
- Books
- Rentals
- Events
- Study Rooms
- Customers
- Invoices

## Security Features

- SQL Injection Prevention
- XSS Protection
- CSRF Protection
- Password Hashing
- Session Security
- Input Validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
