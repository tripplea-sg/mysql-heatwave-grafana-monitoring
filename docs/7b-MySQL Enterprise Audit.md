### MySQL Enterprise Audit Monitoring

MySQL Enterprise Audit provides enterprise-grade MySQL Database Audit. <br>
Please refer to the following for more information on MySQL Enterprise Audit: <br>
https://dev.mysql.com/doc/refman/8.4/en/mysql-enterprise-audit.html

---

#### Implementation Steps

To view the audit configuration tables from Grafana, follow this steps:

**1. Configure Permission**
Go to your audit database schema. Using MySQL HeatWave, the default schema for audit is: "mysql_audit", it may be different with on-premise MySQL Enterprise Edition.
```sql
GRANT SELECT ON mysql_audit.* to 'grafana'@'%';
```
**2. Exposing Audit Data via monitor_tools schema**
Create views within the `monitor_tools` to standardize access to the audit tables:
```sql
CREATE DATABASE IF NOT EXISTS monitor_tools;

GRANT SELECT ON monitor_tools.* to 'grafana'@'%';

GRANT SHOW VIEW ON monitor_tools.* TO 'grafana'@'%';

CREATE VIEW monitor_tools.audit_log_user AS 
SELECT * FROM mysql_audit.audit_log_user;

CREATE VIEW monitor_tools.audit_log_filter AS 
SELECT * FROM mysql_audit.audit_log_filter;
```





#### Dashboard Customization
On Grafana query, do the following query to get the ingested data: <br><br>
**Latest Backup History:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.backup_history 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.backup_history);
```
**Latest Backup Progress:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.backup_progress 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.backup_progress);
```
Once data is populated in repository database, you can design your dashboard for backup monitoring.


