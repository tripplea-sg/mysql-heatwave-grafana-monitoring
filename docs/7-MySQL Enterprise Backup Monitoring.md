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
#### Exposing Backup Data via Performance Schema
Create views within the `performance_schema` to standardize access to the backup tables:
```sql
CREATE VIEW performance_schema.backup_history AS 
SELECT * FROM mysql.backup_history;

CREATE VIEW performance_schema.backup_progress AS 
SELECT * FROM mysql.backup_progress;
```
#### Repository Database Setup
On the MySQL repository database, create dummy tables and corresponding views. This ensures that `backup_history` and `backup_progress` are discoverable within the Grafana console, even before backup data is populated.

```sql
CREATE DATABASE dummy;

CREATE TABLE dummy.backup_history (t int);
CREATE TABLE dummy.backup_progress (t int);

CREATE VIEW performance_schema.backup_history AS 
SELECT * FROM dummy.backup_history;

CREATE VIEW performance_schema.backup_progress AS 
SELECT * FROM dummy.backup_progress;
```
#### Metrics Registration & Dashboard Configuration
1. Navigate to **Control Fleet** to register these new metrics for any registered MySQL EE or MySQL AI targets.
2. Create and customize your own dashboard using the following baseline queries to retrieve the latest backup status:

**Latest Backup History:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.backup_history 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.backup_history);

