# ISP Management App

**Developed with Python 3.13.2**

A Django project for Internet Service Provider management.

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd isp
```

### 2. Create a virtual environment
```bash
pip install --upgrade virtualenv
virtualenv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Make migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser for admin login
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and log in using the superuser credentials you created.

## Screenshots

Below are some screenshots of the project UI:

![Dashboard](static/images/client.png)
![Plan Page](static/images/plan.png)
![Logo](static/images/logo.png)

## Notes
- Ensure you do **not** upload your database or user-uploaded files to GitHub.
- All pre-recorded data and unnecessary files have been removed for a clean start.
- For any issues, please open an issue in the repository.
