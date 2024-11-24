# Cakrawala-Rent-Car-Backend

Cakrawala-Rent-Backend is a Flask-based backend application for managing ID card extraction and related functionalities. This project includes features like user authentication, ID card image upload, OCR-based data extraction, and more.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* Python: Version 3.8 or higher
* pip: Python package manager
* Virtual Environment: Recommended for dependency isolation

## Installation

### 1. Clone the Repository

Navigate to the directory where you want to store the project and clone the repository:

```bash
git clone https://github.com/WawanWidiantara/Cakrawala-Rent-Car-Backend.git
cd project
```

### 2. Create and Activate a Virtual Environment

Create a virtual environment to isolate dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set Environment Variables

Create a `.env` file in the root directory (optional) or set environment variables manually. The `.env` file should look like this:

```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URI=sqlite:///app.db
```

### 2. Configure the Upload Folder

The app saves uploaded files to the `media` directory. Ensure this directory exists and has the proper permissions. Flask will automatically create it if it doesn't exist.

## Running the Application

### 1. Initialize the Database

Run the setup_db.py script to create the required database tables:

```bash
python setup_db.py
```

### 2. Start the Development Server

To run the app locally, use the following command:

```bash
python run.py
```

The app will start at http://127.0.0.1:5000.

## API Endpoints

### Authentication
* POST `/auth/register`: Register a new user
* POST `/auth/login`: Log in and obtain a JWT token

### ID Card Upload
* POST `/upload/id-card`: Upload an ID card image for OCR-based data extraction

### Serve Media Files
* GET `/upload/media/<filename>`: Access uploaded files (e.g., images)

## Testing the Application

### 1. Register a User

Use a tool like Postman or curl to register a new user:

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
-H "Content-Type: application/json" \
-d '{
  "email": "test@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "phone": "123456789"
}'
```

### 2. Log In

Obtain a JWT token:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
-H "Content-Type: application/json" \
-d '{
  "email": "test@example.com",
  "password": "password123"
}'
```

### 3. Upload an ID Card

Upload an ID card image to extract data:

```bash
curl -X POST http://127.0.0.1:5000/upload/id-card \
-F "id_card=@path_to_image.jpg"
```

The server will return the extracted data in JSON format.

## Deployment

### Using Gunicorn

For production, run the app with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Reverse Proxy

For better scalability and SSL handling, configure a reverse proxy with Nginx or Apache.

## Project Structure

```
project/
├── app/
│   ├── __init__.py            # App initialization
│   ├── models.py              # Database models
│   ├── routes/                # API routes
│   │   ├── auth_routes.py     # Authentication routes
│   │   ├── profile_routes.py  # Profile routes
│   │   ├── upload_routes.py   # Upload and OCR routes
│   ├── services/              # Business logic
│   │   ├── ocr_service.py     # OCR extraction logic
├── media/                     # Directory for uploaded files
├── config.py                  # Configuration settings
├── requirements.txt           # Project dependencies
├── run.py                     # Entry point for the app
├── setup_db.py                # Database initialization script
```

## Troubleshooting

### Common Issues

**File Not Found After Upload:**
* Ensure the media directory exists and has proper write permissions
* Verify the absolute path of the saved file

**Cannot Access Uploaded Files:**
* Ensure the route `/upload/media/<filename>` is correctly configured
* Use an absolute path for the UPLOAD_FOLDER

**Database Errors:**
* Run `setup_db.py` to initialize the database tables

## License

This project is licensed under the MIT License.