# GarutVON v2 — Environment Variable Documentation

This document describes the environment variables required to configure **GarutVON v2** in development and production environments.

---

## 1. Database Variables

### `DATABASE_URL`
- **Description:** Connection URL for the database engine.
- **Development Default:** `sqlite:///garutvon.db` (for zero-setup local testing)
- **Production Setting:** Your secure Neon PostgreSQL connection string.
- **Example:** `postgresql://db_user:password@ep-cool-breeze.neon.tech/neondb`

---

## 2. Security Variables

### `SECRET_KEY`
- **Description:** Private key used by Flask to sign session cookies, prevent session tampering, and encrypt state contexts.
- **Requirement:** Must be a cryptographically random, long string in production.

### `JWT_SECRET`
- **Description:** Key used to sign developer portal access tokens.
- **Requirement:** Must be kept private and distinct from the `SECRET_KEY`.

---

## 3. Email Delivery Variables (Mailjet)

To dispatch verify, alert, welcome, and key creation notifications, configure the Mailjet API keys:

### `MAILJET_API_KEY`
- **Description:** Your Mailjet public key credential.

### `MAILJET_SECRET_KEY`
- **Description:** Your Mailjet secure secret credential.

### `MAIL_FROM_EMAIL`
- **Description:** Authorized sender email configured in your Mailjet profile.
- **Example:** `noreply@garutvon.com`

### `MAIL_FROM_NAME`
- **Description:** Display name for outgoing platform notifications.
- **Default:** `GarutVON`

### `SITE_URL`
- **Description:** The canonical public URL for the site used by email links, sitemap generation, and SEO assets.
- **Example:** `https://garutvon.vercel.app`
