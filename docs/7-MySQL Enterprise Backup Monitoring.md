### MySQL Enterprise Backup Monitoring

[MySQL Enterprise Backup](https://www.mysql.com) provides enterprise-grade, hot, online, and non-blocking backup and recovery for Linux, Windows, Mac, and Solaris. It ensures data integrity and operational efficiency without interrupting database availability.

---

#### Implementation Steps

To monitor backup status via Grafana, follow these steps to expose the necessary metadata:

**1. Initialize Backup History**
On your **MySQL AI** or **Enterprise Edition** targets, run at least one backup using Enterprise Backup. This generates the required system tables: `mysql.backup_history` and `mysql.backup_progress`.

**2. Configure Permissions**
Grant `SELECT` access to your monitoring user (e.g., `grafana`).
```sql
GRANT SELECT ON mysql.backup_history TO 'grafana'@'%';
GRANT SELECT ON mysql.backup_progress TO 'grafana'@'%';
```
#### Exposing Backup Data via monitor_tools schema
Create views within the `monitor_tools` to standardize access to the backup tables:
```sql
CREATE DATABASE IF NOT EXISTS monitor_tools;

GRANT SELECT ON monitor_tools.* to 'grafana'@'%';

CREATE VIEW monitor_tools.backup_history AS 
SELECT * FROM mysql.backup_history;

CREATE VIEW monitor_tools.backup_progress AS 
SELECT * FROM mysql.backup_progress;
```

#### Dashboard Customization

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

