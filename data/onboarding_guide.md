# Getting Started: Platform Onboarding Guide

## Welcome to the Platform

This guide will help you get set up and productive within your first 30 minutes.

---

## Step 1: Complete Your Profile

After email verification:
1. Log in at https://platform.com/login
2. Navigate to Account → Profile
3. Fill in:
   - Display name
   - Company name and size
   - Industry (used to surface relevant templates)
   - Time zone (affects scheduled reports and maintenance notifications)

---

## Step 2: Generate Your First API Key

1. Go to Settings → API Keys
2. Click "Generate New Key"
3. Give it a descriptive name (e.g., "Production Backend", "Dev Testing")
4. Select permission scopes:
   - **Read**: Query data, fetch reports
   - **Write**: Create, update, delete records
   - **Admin**: Manage team members, billing, integrations
5. Click "Generate"
6. **Copy the key immediately** — it is shown only once

Store your API key securely using a secrets manager (AWS Secrets Manager, HashiCorp Vault, or environment variables).

---

## Step 3: Make Your First API Call

Test your key with a simple status call:

```bash
curl https://api.platform.com/v1/status \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "status": "operational",
  "version": "2024.1",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

---

## Step 4: Connect Your First Integration

1. Navigate to Integrations → Browse
2. Choose from 50+ available connectors (Slack, GitHub, Salesforce, databases, etc.)
3. Click "Connect" and follow the OAuth or API key flow
4. Configure sync settings and field mappings
5. Test the integration using the "Send Test Event" button

---

## Step 5: Invite Your Team

1. Go to Settings → Team Members
2. Click "Invite Member"
3. Enter their email address
4. Select their role:
   - **Viewer**: Read-only access
   - **Editor**: Can create and modify resources
   - **Admin**: Full access including billing and team management
5. They will receive an invitation email valid for 7 days

---

## Recommended Next Steps

After completing initial setup:
- **Explore Templates**: Pre-built workflows for common use cases (Settings → Templates)
- **Set Up Webhooks**: Receive real-time event notifications (Settings → Webhooks)
- **Review API Docs**: Full reference at https://docs.platform.com/api
- **Join the Community**: Get help and share ideas at https://community.platform.com

---

## Common Onboarding Issues

**Q: My invitation email didn't arrive.**
A: Check spam folder. Add noreply@platform.com to your safe senders list. Resend via Settings → Team Members → Pending Invites.

**Q: My API key returns 401 immediately.**
A: Ensure you're using the full key including the `sk_live_` or `sk_test_` prefix. Keys must be used in the correct environment.

**Q: I can't find the integration I need.**
A: Submit an integration request at https://platform.com/integrations/request. Our team reviews requests monthly.

---

## Support Resources

- Documentation: https://docs.platform.com
- Video tutorials: https://platform.com/tutorials
- Community forum: https://community.platform.com
- Email support: support@platform.com (Pro and Enterprise)
- Live chat: Available 9AM–6PM UTC, Monday–Friday (Enterprise only)
