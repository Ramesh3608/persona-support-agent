# API Authentication Troubleshooting Guide

## Overview
This guide covers common API authentication errors and their resolutions for our SaaS platform REST API.

---

## Error: 401 Unauthorized

### Root Cause
A 401 error means the server could not authenticate the request. This is most commonly caused by:
- Missing or malformed `Authorization` header
- Expired API key or access token
- Incorrect Bearer token format
- API key used in wrong environment (production key used in sandbox)

### Required Header Format
All API requests must include the following HTTP header:

```
Authorization: Bearer <your_api_token>
Content-Type: application/json
X-API-Version: 2024-01
```

### Step-by-Step Resolution

1. **Verify your API key is active**: Log into the developer portal → Settings → API Keys. Confirm the key status shows "Active".
2. **Check token expiry**: Access tokens expire after 3600 seconds (1 hour). Refresh using the `/auth/refresh` endpoint.
3. **Validate header formatting**: The word "Bearer" must have a capital B, followed by exactly one space, then your token.
4. **Confirm environment**: Sandbox tokens begin with `sk_test_`, production tokens begin with `sk_live_`.
5. **Test with cURL**:
   ```bash
   curl -H "Authorization: Bearer sk_live_YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        https://api.platform.com/v1/status
   ```
6. **Check IP allowlist**: If your organization uses IP restrictions, ensure your server IP is whitelisted in Security Settings.

---

## Error: 403 Forbidden

This error means authentication succeeded but the token lacks permission for the requested resource.

### Resolution
- Review your API key's permission scopes in the developer portal
- Upgrade your subscription plan if accessing premium endpoints
- Contact admin to grant additional permissions

---

## Error: 429 Too Many Requests

Rate limit exceeded. Default limits are:
- Free tier: 100 requests/minute
- Pro tier: 1,000 requests/minute
- Enterprise: Unlimited (SLA-based)

Implement exponential backoff with jitter when encountering 429 errors.

---

## Token Refresh Flow

```
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token_here",
  "grant_type": "refresh_token"
}
```

Response returns a new `access_token` valid for 3600 seconds.

---

## Logging and Debugging

Enable verbose logging in your SDK:
```python
import platform_sdk
platform_sdk.set_log_level("DEBUG")
```

API request logs are retained for 30 days and accessible via the developer portal under Logs → API Requests.
