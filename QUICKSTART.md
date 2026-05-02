# Quick Start Guide

## Prerequisites
- Python 3.11+
- MySQL 9.6+
- Gmail account with App Password enabled

## Step 1 — Clone the repo
```bash
git clone https://github.com/yourusername/errortranslator.git
cd errortranslator
```

## Step 2 — Install dependencies
```bash
pip install flask flask-cors flask-mail mysql-connector-python
```

## Step 3 — Setup MySQL
Open MySQL Workbench and run:
```sql
CREATE DATABASE error_translator;
USE error_translator;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  iwrite INT DEFAULT 0,
  created_by VARCHAR(100),
  email VARCHAR(255)
);

CREATE TABLE error_codes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  error_no VARCHAR(6) NOT NULL UNIQUE,
  display_message VARCHAR(500) NOT NULL,
  updated_date_time DATETIME DEFAULT CURRENT_TIMESTAMP
  ON UPDATE CURRENT_TIMESTAMP,
  updated_by VARCHAR(100)
);

CREATE TABLE error_lookup_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  error_no VARCHAR(6) NOT NULL,
  looked_up_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, iwrite, created_by)
VALUES ('admin', 'admin123', 1, 'YourName');
```

## Step 4 — Configure app.py
Open app.py and fill in your details:
```python
# Email config
app.config['MAIL_USERNAME'] = 'your_gmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_gmail_app_password'

# MySQL config
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_mysql_password',
        database='error_translator'
    )
```

## Step 5 — Run
```bash
python app.py
```

## Step 6 — Open frontend
Open index.html in browser or use Live Server in VS Code.

## Default Login
- Username: `admin`
- Password: `admin123`

## Notes
- Change admin password after first login
- For deployment see Render + Railway + Netlify