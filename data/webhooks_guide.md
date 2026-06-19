# Webhooks Configuration & Troubleshooting

## Overview

Webhooks allow our platform to send real-time HTTP POST notifications to your server whenever specific events occur in your account. This eliminates the need for polling.

---

## Setting Up a Webhook

1. Navigate to Settings → Webhooks → Add Endpoint
2. Enter your HTTPS endpoint URL (HTTP is not accepted for security reasons)
3. Select events to subscribe to (see Event Types below)
4. Click "Save" and note your webhook secret

### Webhook Secret

Each webhook endpoint has a unique signing secret (prefixed with `whsec_`). Use this to verify that incoming requests originate from our platform:

```python
import hmac
import hashlib

def verify_webhook_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    expected_sig = hmac.new(
        secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature_header)
```

---

## Event Types

| Event | Description |
|-------|-------------|
| `user.created` | New user registered |
| `user.deleted` | Account deleted |
| `payment.succeeded` | Payment processed successfully |
| `payment.failed` | Payment declined |
| `integration.connected` | New integration connected |
| `integration.error` | Integration error occurred |
| `api.rate_limit_exceeded` | Rate limit hit |
| `data.sync.completed` | Data sync finished |
| `incident.created` | New incident reported |
| `incident.resolved` | Incident resolved |

---

## Webhook Payload Format

```json
{
  "id": "evt_01H9XKQM4V3P2NQRS7TBW",
  "type": "payment.succeeded",
  "created": 1705320000,
  "data": {
    "object": {
      "amount": 4900,
      "currency": "usd",
      "customer_id": "cust_01H9XK",
      "invoice_id": "inv_01H9XL"
    }
  }
}
```

---

## Retry Logic

If your endpoint returns a non-2xx status code, we retry delivery:
- Retry 1: After 5 minutes
- Retry 2: After 30 minutes
- Retry 3: After 2 hours
- Retry 4: After 8 hours
- Retry 5: After 24 hours

After 5 failed attempts, the event is marked as failed and no further retries occur. Failed events are visible in Settings → Webhooks → Failed Events.

---

## Common Webhook Issues

### Webhooks Not Being Received

1. **Check endpoint URL**: Must be HTTPS and publicly accessible. `localhost` URLs will not work in production.
2. **Check response codes**: Your endpoint must return HTTP 200 within 30 seconds or we consider it failed.
3. **Check firewall rules**: Allow inbound requests from our IP ranges (34.102.0.0/16, 35.191.0.0/16).
4. **Review delivery logs**: Settings → Webhooks → Delivery Logs shows all attempted deliveries and responses.

### Duplicate Events

In rare cases (network issues), the same event may be delivered more than once. Use the `id` field to deduplicate:

```python
processed_event_ids = set()

def handle_webhook(event):
    if event['id'] in processed_event_ids:
        return  # Already processed
    processed_event_ids.add(event['id'])
    # Process event...
```

### Signature Verification Failing

- Ensure you're using the raw request body bytes (do not parse/re-serialize before verification)
- The signature is in the `X-Platform-Signature` HTTP header
- The secret must match the one shown for that specific endpoint in Settings → Webhooks

---

## Testing Webhooks

Use the "Send Test Event" button in Settings → Webhooks to send a sample payload. For local development, use ngrok to expose your local server:

```bash
ngrok http 3000
# Use the https://xxx.ngrok.io URL as your webhook endpoint during testing
```
