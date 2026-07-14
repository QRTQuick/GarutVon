# GarutVON v2 — Universal File Productivity Platform

GarutVON is a premium, universal file productivity platform designed to help individuals, businesses, and developers work efficiently. Users can convert files, process data, automate workflows, and integrate GarutVON into their own software through high-performance cloud APIs.

Version 1 focuses on **Image Conversion**. All other planned services are present in the UI and backend and are clearly marked as **Coming Soon** with clean, standardized programmatic responses.

---

## 🚀 Key Features

- **High-Performance Image Converter (Active)**: Fast conversion across major formats:
  - PNG &rarr; JPG, WEBP, BMP, TIFF, ICO
  - JPG/JPEG &rarr; PNG, WEBP
  - WEBP, BMP, GIF (first frame), TIFF, ICO &rarr; PNG
- **Automated Developer APIs (Active)**: Secure, hashed developer keys portal. Convert files programmatically via FastAPI endpoints on port `8000`.
- **Happer Donations Hub (Active)**: Seamless, secure integration with **Happer** to fuel independent SaaS hosting and infrastructure.
- **Admin Dashboard Console (Active)**: Comprehensive logs, active user management directories, live toggles for feature flags, and CSV-exportable donation ledgers.
- **Secure Authentication & Security (Active)**: Complete account verification, password resets, active login alerts, session managers, secure cookie-based CSRF checks, and premium Argon2 password hashing.

---

## 🛠️ Technology Stack

- **Frontend:** Pure HTML5, CSS3 Variables, Glassmorphism design elements, Canvas particle grids, and Vanilla JavaScript (ES6). No bloated frameworks or heavy libraries.
- **Backend:** Python, Flask (Website & UI API), FastAPI (Developer APIs), and Gunicorn/Uvicorn.
- **Database:** Neon PostgreSQL (with SQLite compatibility for zero-setup local dev/testing), mapped using **SQLAlchemy ORM**.
- **Email Delivery:** Mailjet.

---

## 📁 Directory Structure

```text
garutvon-v2/
├── backend/            # Python backend APIs & launchers
│   ├── services/       # Core business services (Auth, Converter, Payments, Emails)
│   ├── web.py          # Flask website server
│   ├── main.py         # FastAPI developer server
│   └── config.py       # Configuration environment manager
├── database/           # Models & databases creation files
│   └── models.py       # SQLAlchemy ORM schemas & tables seeding
├── frontend/           # Static premium visual assets
│   ├── css/            # Style sheets (global resets, dashboards, 3D scenes)
│   ├── js/             # Script modules (auth controllers, Canvas particles, tilt effects)
│   └── index.html      # Central platform homepage
├── docs/               # Detailed architectural Guides
├── tests/              # Platform unit verification suites
├── uploads/            # Temporary incoming file uploads directory
└── outputs/            # Processed converted files storage directory
```

---

## ⚡ Quickstart

1. **Configure Environment Variables**: See `.env.example` or the Environment Guide for details.
2. **Install Packages**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch Server**:
   ```bash
   python run.py
   ```
4. **Access Platorm**:
   - **Website**: `http://localhost:5000`
   - **API Docs**: `http://localhost:8000/docs`

---

## 📖 Complete Guides

For detailed guides, please read the documentation located inside the `docs/` folder:
- 🛠️ [Local Installation Guide](docs/INSTALLATION.md)
- 🚀 [Production Deployment Guide](docs/DEPLOYMENT.md)
- 🔐 [Developer API Integration Docs](docs/API_DOCUMENTATION.md)
- 📊 [Database Schema Layout](docs/DATABASE_SCHEMA.md)
- 💻 [Internal Developer Guide](docs/DEVELOPER_GUIDE.md)
- 🤝 [Contribution Philosophy](docs/CONTRIBUTION.md)
- ⚙️ [Environment Configurations](docs/ENVIRONMENT.md)
