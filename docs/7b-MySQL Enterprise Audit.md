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
Create views within the `monitor_tools` to standardize access to the audit data:
```sql
CREATE VIEW monitor_tools.audit_data as
SELECT
  jt.ts,
  jt.event_id,
  jt.class_name,
  jt.event_name,
  jt.connection_id,
  jt.account_user,
  jt.account_host,
  jt.login_ip,
  COALESCE(jt.db_conn, jt.db_table) AS db_name,
  jt.table_name,
  COALESCE(jt.sql_cmd_general, jt.sql_cmd_table) AS sql_command,
  COALESCE(jt.query_general, jt.query_table) AS query_text,
  jt.status_code
FROM JSON_TABLE(
  audit_log_read(
  audit_log_read_bookmark()
  ),
  '$[*]' COLUMNS (
    ts               DATETIME      PATH '$.timestamp' NULL ON EMPTY,
    event_id         BIGINT        PATH '$.id' NULL ON EMPTY,
    class_name       VARCHAR(32)   PATH '$.class' NULL ON EMPTY,
    event_name       VARCHAR(32)   PATH '$.event' NULL ON EMPTY,
    connection_id    BIGINT        PATH '$.connection_id' NULL ON EMPTY,
    account_user     VARCHAR(128)  PATH '$.account.user' NULL ON EMPTY,
    account_host     VARCHAR(255)  PATH '$.account.host' NULL ON EMPTY,
    login_ip         VARCHAR(64)   PATH '$.login.ip' NULL ON EMPTY,
    db_conn          VARCHAR(128)  PATH '$.connection_data.db' NULL ON EMPTY,
    db_table         VARCHAR(128)  PATH '$.table_access_data.db' NULL ON EMPTY,
    table_name       VARCHAR(128)  PATH '$.table_access_data.table' NULL ON EMPTY,
    sql_cmd_general  VARCHAR(64)   PATH '$.general_data.sql_command' NULL ON EMPTY,
    sql_cmd_table    VARCHAR(64)   PATH '$.table_access_data.sql_command' NULL ON EMPTY,
    query_general    TEXT          PATH '$.general_data.query' NULL ON EMPTY,
    query_table      TEXT          PATH '$.table_access_data.query' NULL ON EMPTY,
    status_code      INT           PATH '$.general_data.status' NULL ON EMPTY
  )
) AS jt
WHERE jt.ts IS NOT NULL
ORDER BY jt.ts DESC, jt.event_id DESC;
```
Please examine the monitor_tools.audit_data and implement WHERE clause to the view when applicable to limit data volume ingested by the MySQL repository. 

#### Dashboard Customization
On Grafana query, do the following query to get the ingested data: <br><br>
**Latest audit_log_user:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.audit_log_user 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.audit_log_user);
```
**Latest audit_log_filter:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.audit_log_filter 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.audit_log_filter);
```
**Latest audit log data:**
```sql
SELECT *
FROM `${compartment}#${display_name}`.audit_data
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.audit_log_filter);
``
Once data is populated in repository database, you can design your dashboard for backup monitoring.


