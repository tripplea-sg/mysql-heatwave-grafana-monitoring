### MySQL Enterprise Firewall Monitoring

MySQL Enterprise Firewall provides enterprise-grade MySQL Database Firewall. <br>
Please refer to the following for more information on MySQL Enterprise Firewall: <br>
https://dev.mysql.com/doc/refman/8.4/en/firewall-usage.html

---

#### Implementation Steps

To view the Firewall configuration tables from Grafana, follow this steps:
**1. Exposing Firewall User Data via monitor_tools schema**
Create views within the `monitor_tools` to standardize access to the audit tables:
```sql
CREATE DATABASE IF NOT EXISTS monitor_tools;

GRANT SELECT ON monitor_tools.* to 'grafana'@'%';

GRANT SHOW VIEW ON monitor_tools.* TO 'grafana'@'%';

CREATE VIEW monitor_tools.firewall_users AS 
SELECT * FROM information_schema.mysql_firewall_users;

```
#### Dashboard Customization
On Grafana query, do the following query to get the ingested data: <br><br>
**Latest firewall_users:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.firewall_users 
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.firewall_users);
```
**Latest Firewall Statistics:**
```sql
SELECT * 
FROM `${compartment}#${display_name}`.global_variables  
WHERE logtime = (SELECT MAX(logtime) FROM `${compartment}#${display_name}`.global_variables)
AND VARIABLE_NAME LIKE 'Firewall%';
```
Once data is populated in repository database, you can design your dashboard for firewall log monitoring.
