# GarutVON v2 — Installation Guide

This document describes how to set up the **GarutVON v2** SaaS platform in a local development environment.

## Prerequisites

Ensure you have the following software installed on your machine:
- **Python (v3.10 or higher)**
- **Git**
- **pip** (Python package installer)
- *(Optional)* **PostgreSQL** (with Neon compatibility, otherwise defaults to local SQLite).

## Step-by-Step Installation

### 1. Clone the Repository
Clone the repository to your local system and navigate to the project directory:
```bash
git clone https://github.com/your-username/garutvon-v2.git
cd garutvon-v2
```

### 2. Configure Your Virtual Environment
Create a clean Python virtual environment to isolate project packages:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
Install all required production and testing dependencies:
```bash
pip install -r requirements.txt
```
*(If no requirements.txt is provided, refer to the next step which creates/updates it).*

### 4. Set Up Environment Variables
Create a `.env` file in the root directory based on the environment guide:
```env
# Database configuration
DATABASE_URL=postgresql://<username>:<password>@<host>/<database>?sslmode=require

# Security
SECRET_KEY=garutvon-super-secret-dev-key-123456
JWT_SECRET=garutvon-jwt-secret-key-987654

# Mailjet Configuration
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_SECRET_KEY=your_mailjet_secret_key
MAIL_FROM_EMAIL=noreply@garutvon.com
MAIL_FROM_NAME=GarutVON

# Public site URL for email links and SEO assets
SITE_URL=https://garutvon.vercel.app
```

### 5. Launch the Platform
Start both the Flask web server (Website & Dashboard) and the FastAPI developer api instance simultaneously using the shared launcher:
```bash
python3 run.py
```
Upon successful launch, the terminal will display:
- **Website & User Dashboard:** `http://localhost:5000`
- **Developer programmatic API:** `http://localhost:8000`

### 6. Admin Account Seeding
By default, the system automatically seeds a secure SuperAdmin account on startup if the database is empty:
- **Admin Email:** `admin@garutvon.com`
- **Admin Password:** `AdminSecurePass2026!`
Log in using these credentials at `http://localhost:5000/login` to access the full System Administrator Panel.
