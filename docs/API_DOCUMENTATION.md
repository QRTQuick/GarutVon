# GarutVON v2 — Programmatic Developer API Documentation

Integrate high-speed image processing and productivity tools programmatically using the official GarutVON cloud gateway.

## Base URL
- **Production API:** `https://api.garutvon.com/api/v1`
- **Local Testing:** `http://localhost:8000/api/v1`

---

## Authentication

Every API call must include your private developer key in the request headers:
- Header: `X-API-Key`
- Format: `gv_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Example cURL:
```bash
curl -H "X-API-Key: gv_my_secret_key" https://api.garutvon.com/api/v1/usage
```

---

## Endpoints

### 1. Perform Image Conversion
`POST /convert/image`

Converts a raw source image and returns the compiled binary format in the response payload.

**Headers:**
- `X-API-Key`: Your developer API Key.

**Form Parameters (Multipart/form-data):**
- `file`: The raw binary source image file (Max size 16MB).
- `format`: Target output format (supports `PNG`, `JPG`, `WEBP`, `BMP`, `TIFF`, `ICO`).

**Responses:**
- `200 OK`: Transports raw binary stream corresponding to the target image format.
- `400 Bad Request`: Returns structured JSON containing validation error messages:
  ```json
  {
    "detail": "Invalid or corrupt image file: Cannot verify integrity."
  }
  ```
- `429 Too Many Requests`: Triggered when exceeding weekly subscription quotas:
  ```json
  {
    "detail": "Weekly programmatic allocation limit exceeded. Current plan limit is 10 conversions/week."
  }
  ```

---

### 2. View Usage Analytics
`GET /usage`

Returns programmatic usage metrics, response latencies, and transaction histories.

**Headers:**
- `X-API-Key`: Your developer API Key.

**Response Example (200 OK):**
```json
{
  "status": "success",
  "analytics": {
    "total_calls_tracked": 142,
    "successful_requests": 140,
    "failed_requests": 2,
    "average_latency_ms": 115
  },
  "usage_logs": [
    {
      "endpoint": "/api/v1/convert/image",
      "method": "POST",
      "status_code": 200,
      "response_time_ms": 135,
      "date": "2026-07-12 11:32:15"
    }
  ]
}
```

---

### 3. Future Services Programmatic Hooks
The endpoints below are under active development. Querying them will return a structured `Coming Soon` message:
- `POST /convert/pdf`
- `POST /convert/ocr`
- `POST /convert/document`
- `POST /convert/translate`
- `POST /convert/background-removal`

**Response Example (200 OK):**
```json
{
  "status": "coming_soon",
  "message": "This service is currently under development."
}
```
