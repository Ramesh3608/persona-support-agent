# Database Integration Troubleshooting Guide

## Supported Database Integrations

Our platform supports native connectors for:
- PostgreSQL 12+
- MySQL 8.0+
- MongoDB 5.0+
- Redis 6.0+
- Microsoft SQL Server 2019+
- Amazon RDS (all supported engines)
- Google Cloud SQL

---

## Common Connection Errors

### Error: Connection Refused (ECONNREFUSED)

**Root Cause:** The database server is not accepting connections on the specified port.

**Diagnostic Steps:**
1. Verify the database server is running:
   ```bash
   # PostgreSQL
   pg_ctl status -D /var/lib/postgresql/data
   
   # MySQL
   systemctl status mysql
   ```
2. Confirm the port is open and listening:
   ```bash
   netstat -tlnp | grep 5432  # PostgreSQL default port
   netstat -tlnp | grep 3306  # MySQL default port
   ```
3. Check firewall rules allow inbound connections from platform IP ranges:
   - 34.102.0.0/16
   - 35.191.0.0/16

---

### Error: SSL/TLS Handshake Failure

**Root Cause:** SSL certificate mismatch or TLS version incompatibility.

**Resolution:**
1. Ensure your database server supports TLS 1.2 or higher
2. Upload your CA certificate in Integration Settings → SSL Certificates
3. For self-signed certificates, enable "Allow Self-Signed Certificates" in the connector settings
4. Verify certificate CN/SAN matches your database hostname exactly

---

### Error: Internal Server Error During Database Write

**Root Cause:** This typically indicates one of the following:
- Schema mismatch between expected and actual table structure
- Insufficient database user permissions
- Database disk space exhaustion
- Deadlock or transaction timeout

**Step-by-Step Resolution:**

1. **Check database logs** for the exact error:
   ```bash
   tail -n 100 /var/log/postgresql/postgresql.log
   ```

2. **Verify user permissions:**
   ```sql
   -- PostgreSQL
   SELECT grantee, privilege_type 
   FROM information_schema.role_table_grants 
   WHERE table_name='your_table';
   ```

3. **Check disk space:**
   ```bash
   df -h /var/lib/postgresql/
   ```

4. **Check for active locks:**
   ```sql
   SELECT pid, query, state, wait_event_type, wait_event
   FROM pg_stat_activity
   WHERE state != 'idle';
   ```

5. **Validate schema:** Compare your integration schema definition with the actual database schema using our Schema Validator tool in Integration Settings.

---

## Connection String Format

### PostgreSQL
```
postgresql://username:password@hostname:5432/database_name?sslmode=require
```

### MySQL
```
mysql://username:password@hostname:3306/database_name?ssl-mode=REQUIRED
```

### MongoDB
```
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true
```

---

## Performance Optimization

### Connection Pooling
Always use connection pooling in production. Recommended pool sizes:
- Small workload: min=2, max=10
- Medium workload: min=5, max=20
- High throughput: min=10, max=50

Configure in Integration Settings → Advanced → Connection Pool.

### Query Timeout Settings
Default query timeout: 30 seconds
Maximum allowed timeout: 300 seconds

Adjust in the connector configuration:
```json
{
  "query_timeout_ms": 30000,
  "connection_timeout_ms": 10000,
  "idle_timeout_ms": 600000
}
```

---

## Data Sync Troubleshooting

If your database sync is failing or showing stale data:
1. Check the sync schedule in Integration Settings → Sync Schedule
2. Review sync logs under Integrations → Logs → Database Sync
3. Manually trigger a sync via the "Force Sync" button
4. If errors persist, disable and re-enable the integration to reset the sync state
