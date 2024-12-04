# Backend Project README

## Overview

This is the backend for an e-commerce application developed using Flask, MySQL, and Zappa for serverless deployment on AWS Lambda. It supports essential functionalities such as product management, cart handling, user authentication, and API integration for enhanced product information.

## Features

- **User Authentication**: Supports user login and registration with hashed password storage.
- **Cart Management**: Allows users to save and retrieve their cart items, and perform checkout operations.
- **Product Management**: Provides endpoints for adding, updating, and retrieving product data.
- **Serverless Deployment**: Deployed on AWS Lambda using Zappa for scalable serverless execution.
- **API Integration**: Integrates with external APIs to retrieve additional product information.

---

## Project Structure

```
.
├── app.py                  # Flask application entry point
├── modules/
│   ├── functions.py        # Core business logic and database interaction
│   ├── api_request.py      # Handles external API interactions (e.g., RapidAPI)
├── requirements.txt        # Python dependencies
├── zappa_settings.json     # Configuration for Zappa deployment
├── .env                    # Environment variables (ignored in Git)
└── README.md               # Project documentation
```

---

## Prerequisites

### Local Development
- Python 3.12
- MySQL database
- Virtual environment (`venv`)

### Deployment
- AWS account
- Zappa installed globally (`pip install zappa`)

---

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File
Add the following to `.env` (replace placeholders with actual values):
```plaintext
DB_HOST=<your-db-host>
DB_NAME=<your-database-name>
DB_USERNAME=<your-username>
DB_PASSWORD=<your-password>
x-rapidapi-key=<your-rapidapi-key>
x-rapidapi-host=<your-rapidapi-host>
```

### 5. Initialize the Database
Ensure your MySQL database is set up and contains the required schema for tables like `product`, `cart`, and `users`.

---

## Running Locally

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

3. Visit `http://127.0.0.1:8080` in your browser or use an API testing tool like Postman to interact with the backend.

---

## Deployment with Zappa

### 1. Configure `zappa_settings.json`
Create a `zappa_settings.json` file with the following structure:
```json
{
    "dev": {
        "app_function": "app.app",
        "aws_region": "<your-aws-region>",
        "profile_name": null,
        "project_name": "<your-project-name>",
        "runtime": "python3.12",
        "s3_bucket": "<your-s3-bucket>",
        "environment_variables": {
            "DB_HOST": "<your-db-host>",
            "DB_NAME": "<your-db-name>",
            "DB_USERNAME": "<your-username>",
            "DB_PASSWORD": "<your-password>",
            "x-rapidapi-key": "<your-rapidapi-key>",
            "x-rapidapi-host": "<your-rapidapi-host>"
        }
    }
}
```

### 2. Deploy to AWS
Deploy the project to AWS Lambda using Zappa:
```bash
zappa deploy dev
```

### 3. Update Deployment
After making changes to the backend:
```bash
zappa update dev
```

### 4. Test API
Visit the API Gateway endpoint URL provided by Zappa to verify deployment.

---

## API Endpoints

### **User Authentication**
- **POST** `/login/` – Login an existing user.
- **POST** `/logout/` – Log out a user.

### **Product Management**
- **GET** `/` – Retrieve all products.
- **POST** `/add_product` – Add a new product.
- **POST** `/change_name` – Update product name.
- **POST** `/change_price` – Update product price.

### **Cart Management**
- **POST** `/cart/save` – Save cart items for a user.
- **GET** `/cart/<int:user_id>` – Retrieve cart items for a user.
- **POST** `/checkout` – Checkout a user's cart.

---

## Error Handling

- All endpoints return structured JSON error messages with appropriate HTTP status codes.
- Common errors are logged in the AWS Lambda environment or in the local console.

---

## Known Issues and Debugging

1. **Environment Variables Not Loading**
   - Ensure `.env` is correctly configured and `dotenv` is installed.
   - For AWS Lambda, use `zappa_settings.json` to set environment variables.

2. **Database Connection Issues**
   - Always verify MySQL credentials first, then check for connection allowance from your development machine or Lambda's IP.

3. **Module Import Errors**
   - Ensure all required modules are installed and properly referenced in the project structure.

---

## .gitignore

The `.gitignore` file should include the following:
```plaintext
venv/
.env
zappa_settings.json
__pycache__/
*.pyc
```

---

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

## Contributors

- **Richard Palestri** – Backend Developer
- **Ilir Krasniqi** - Backend Developer , SQL Developer
- **Dashamir Brkani** – Frontend Developer , Backend Developer

For any issues or questions, feel free to contact the contributors or raise an issue on the project repository.