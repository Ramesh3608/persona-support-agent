# General Troubleshooting FAQ

## Platform Loading Issues

**Q: The platform won't load in my browser. What should I do?**

Follow these steps in order:
1. Check the status page at https://status.platform.com to see if there is an active incident
2. Clear your browser cache and cookies (Ctrl+Shift+Delete on Windows, Cmd+Shift+Delete on Mac)
3. Try opening the platform in an incognito/private browsing window
4. Disable browser extensions, especially ad blockers
5. Try a different browser (Chrome, Firefox, Edge, Safari)
6. Check your internet connection — run a speed test at https://fast.com
7. If on a corporate network, ask your IT team if platform.com is blocked by your firewall or proxy

If none of the above works, contact support with your browser version, OS, and a screenshot of the error.

---

## Login Problems

**Q: I keep getting "Invalid credentials" even though I'm sure my password is correct.**

- Make sure Caps Lock is off
- Try copying and pasting your password to avoid typing errors
- Use the "Forgot Password" flow to reset your password
- If using SSO (Single Sign-On), ensure you're logging in through your company's SSO portal, not the standard login page
- Check that you're using the correct email address (work email vs personal email)

**Q: My account is locked. How do I unlock it?**

Accounts are locked after 10 consecutive failed login attempts. The lock automatically lifts after 30 minutes. Alternatively:
- Use the "Forgot Password" flow to reset and unlock simultaneously
- Contact support@platform.com with your account email to unlock immediately

---

## Data Not Appearing

**Q: I created records via the API but they're not showing in the dashboard.**

1. Check that your API call returned a successful 201 or 200 response
2. Refresh the dashboard page (Ctrl+R or Cmd+R)
3. Confirm you're looking at the correct workspace/organization
4. Check if data filters are applied — click "Clear Filters" in the top right
5. If syncing from an integration, check the last sync time under Integrations → [Integration Name] → Last Sync

---

## Email Notifications Not Arriving

**Q: I'm not receiving platform notification emails.**

1. Check your spam/junk folder
2. Add the following domains to your safe senders list:
   - noreply@platform.com
   - notifications@platform.com
   - incidents@platform.com
3. Check your notification preferences: Account → Notifications → Email Settings
4. If using a corporate email, ask your IT team to whitelist platform.com mail servers
5. Verify your email address is correct in Account → Profile

---

## Export / Download Issues

**Q: My data export is not downloading.**

1. Wait a few minutes — large exports can take up to 10 minutes to prepare
2. Check the exports queue in Settings → Data Export → Export History
3. Try downloading from a different browser
4. Ensure pop-ups are not blocked (exports open in a new window/tab)
5. Maximum export size is 1 million rows. For larger datasets, use the API with pagination.

---

## Integration Sync Issues

**Q: My integration stopped syncing. Data is stale.**

1. Go to Integrations → [Integration Name] → Status
2. Check the error message displayed on the integration card
3. Common causes:
   - OAuth token expired → Click "Reconnect" to re-authorize
   - API rate limit on the third-party service → Sync will resume automatically when limit resets
   - Schema change in source data → Review field mappings
4. Click "Force Sync" to trigger an immediate sync attempt
5. Review sync logs under Integrations → Logs

---

## Performance Issues

**Q: The platform feels slow. What can I do?**

1. Check https://status.platform.com for degraded performance notices
2. Check your browser: close unused tabs, clear cache
3. If using the API, check if you're making unoptimized requests (see Performance Optimization Guide)
4. Test from a different network to rule out local network issues
5. If slowness is isolated to a specific feature, report it to support with timing details

---

## Getting More Help

- **Knowledge Base**: https://help.platform.com
- **Community Forum**: https://community.platform.com  
- **Email Support**: support@platform.com (Pro/Enterprise; 24-hour response SLA)
- **Live Chat**: Available Monday–Friday 9AM–6PM UTC for Enterprise customers
- **Urgent Incidents**: For Severity 1 issues, use the "Report Critical Issue" button in the platform footer
