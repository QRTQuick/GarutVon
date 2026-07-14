# GarutVON v2 — Developer Guide

This guide is designed for software engineers working on the **GarutVON v2** platform. It outlines the project's software design philosophy, coding standards, and step-by-step procedures for extending conversion utilities.

---

## 1. Architectural Philosophy

GarutVON follows clean, decoupled architecture principles:
- **SOLID Design Principles:** Every class or module has a single responsibility.
- **ORM-based Data Mapping:** Direct database modifications are prohibited. All database interactions utilize SQLAlchemy models.
- **Cryptographic Security:** API keys are never stored in plain text. SHA-256 hashes are verified securely in real time. Passwords utilize robust **Argon2** hashing.

---

## 2. Shared Services Directory

Key logic is isolated inside `backend/services/`:
- **`AuthService`**: Handles session cookies, CSRF tokens, email tokens, and JWT generations.
- **`ImageConverterService`**: Handles header checks, input validations, and Pillow conversions.
- **`PaymentService`**: Modular registry class facilitating rapid payment additions (Happer, Stripe, etc.).
- **`EmailService`**: Integrates Mailjet triggers with local development print logs simulation.

---

## 3. Extending Conversion Services

To add a new service (e.g., PDF Conversion):
1. **Define a Model/State:** Ensure corresponding history types exist inside `ConversionHistory`.
2. **Implement service logic:** Create `backend/services/pdf_converter.py` containing clean Pillow/PyPDF formatting classes.
3. **Register Route inside Flask (`web.py`)**: Re-route incoming requests to your PDF processor.
4. **Define Developer APIs in FastAPI (`main.py`)**: Support programmatic conversions on port `8000`.
5. **Add Admin Feature Flag:** Seed a new feature flag in `database/models.py` to allow live-toggling of your module in production!
