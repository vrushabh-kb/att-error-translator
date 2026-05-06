# Error Translator — AT&T EBB Project

A full-stack web admin tool that translates cryptic US Government error codes into human-readable messages for AT&T's Emergency Broadband Benefit (EBB) program.

## What it does
- Admin login with Read/Write access control
- CRUD operations on error code mappings
- Public lookup API for AT&T portal integration
- Analytics dashboard with bar chart
- Register new users with email notification
- Forgot password via email
- Export error codes to CSV
- Search and filter error codes

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python Flask
- **Database:** MySQL
- **Email:** Flask-Mail with SENDGRID MAIL

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/errors | Get all error codes |
| POST | /api/errors | Add new error code |
| PUT | /api/errors/<error_no> | Update error code |
| DELETE | /api/errors/<error_no> | Delete error code |
| POST | /api/login | User login |
| POST | /api/register | Register new user |
| POST | /api/change-password | Change password |
| POST | /api/forgot-password | Forgot password |
| GET | /api/lookup/<error_no> | Public lookup API |
| GET | /api/analytics | Analytics data |

## Setup Instructions
See QUICKSTART.md
