# GarutVON v2 — Database Schema Documentation

This document describes the normalized database schema structure designed for **GarutVON v2**. The database is powered by **Neon PostgreSQL** and mapped using **SQLAlchemy ORM**.

---

## Normalized Tables

### 1. `users`
Tracks primary client account records and preferences.
- `id` (Integer, Primary Key)
- `email` (String, Unique, Indexed) — User's electronic mail.
- `password_hash` (String) — Secure Argon2 password hash.
- `full_name` (String) — User's name.
- `is_verified` (Boolean) — Status of email verification.
- `email_promo_pref` (Boolean) — Product updates newsletter subscription.
- `email_security_pref` (Boolean) — security alerts mailings.
- `created_at` (DateTime)
- `updated_at` (DateTime)

### 2. `sessions`
First-party browser session tokens.
- `id` (Integer, Primary Key)
- `session_token` (String, Unique, Indexed)
- `user_id` (Integer, Foreign Key to `users.id`)
- `ip_address` (String) — Login client's IP.
- `user_agent` (String) — Browser user agent context.
- `expires_at` (DateTime)

### 3. `api_keys`
Programmatic developer keys.
- `id` (Integer, Primary Key)
- `key_prefix` (String) — visible prefix like `gv_xxxx`.
- `key_hash` (String, Unique, Indexed) — SHA-256 secure hashed representation.
- `user_id` (Integer, Foreign Key to `users.id`)
- `name` (String) — Descript description for key identification.
- `created_at` (DateTime)
- `last_used_at` (DateTime)
- `is_active` (Boolean)

### 4. `api_usage`
Tracks performance and query auditing logs of keys.
- `id` (Integer, Primary Key)
- `api_key_id` (Integer, Foreign Key to `api_keys.id`)
- `endpoint` (String)
- `method` (String)
- `status_code` (Integer)
- `ip_address` (String)
- `response_time_ms` (Integer) — Latency measurement.
- `created_at` (DateTime)

### 5. `conversion_history`
Maintains records of all file processing tasks.
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key to `users.id`)
- `api_key_id` (Integer, Foreign Key to `api_keys.id`)
- `service_type` (String) — e.g. `image_converter`.
- `input_file_name` (String)
- `input_file_size` (Integer)
- `input_format` (String)
- `output_format` (String)
- `status` (String) — e.g. `completed`, `failed`.
- `download_token` (String, Unique, Indexed) — Token for secure retrieval.
- `created_at` (DateTime)

### 6. `donations`
Keeps track of voluntary support donations made via Happer.
- `id` (Integer, Primary Key)
- `donation_id` (String, Unique, Indexed) — External payment ID.
- `transaction_ref` (String, Unique, Indexed) — Cryptographic reference.
- `user_id` (Integer, Foreign Key to `users.id`) — Optional registered link.
- `amount` (Float) — Monetary contribution.
- `currency` (String)
- `payment_status` (String) — e.g., `completed`, `pending`.
- `payment_provider` (String) — Defaults to `Happer`.
- `donor_name` (String)
- `donor_message` (Text)
- `created_at` (DateTime)

### 7. `feature_flags`
Configurable parameters for progressive feature rollouts.
- `id` (Integer, Primary Key)
- `name` (String, Unique, Indexed) — e.g. `pdf_conversion`.
- `description` (String)
- `is_enabled` (Boolean)
- `updated_at` (DateTime)

---

## Schema Seeding Helper

On initial engine startup, the `database/models.py` seeding helper automatically populates crucial platform dependencies:
- Default Subscription Plans (`Free Plan`, `Developer Pro`).
- Initial Feature Flags (`pdf_conversion`, `ocr`, `ai_chat`, etc.).
- Admin Role Permissions structures.
- Default SuperAdmin account credentials.
