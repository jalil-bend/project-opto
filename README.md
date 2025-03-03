# CLINIQUE Medical Records Management System

## Project Overview
CLINIQUE is a comprehensive medical records management system designed to streamline record-keeping, access, and management for healthcare professionals.

## Project Structure
- `core/`: Core application configuration
- `medical_records/`: Medical records management app
- `records/`: Record-related functionality
- `users/`: User authentication and management
- `static/`: Static files (CSS, JavaScript)
- `templates/`: HTML templates

## Prerequisites
- Python 3.8+
- Django
- Virtual Environment

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/clinique.git
cd clinique
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## Key Features
- User authentication
- Medical record upload
- Researcher dashboard
- Professional record management

## Security Notes
- Always keep `SECRET_KEY` confidential
- Use environment variables for sensitive information

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
