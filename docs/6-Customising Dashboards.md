### 💡 Building Custom Dashboards

By reviewing the sample queries provided in the three dashboard templates, you can easily understand the underlying data architecture. This approach allows you to:

*   **Modify Existing Templates:** Adjust thresholds or time windows to better suit your specific workload requirements.
*   **Create New Views:** Build your own custom dashboards by writing queries against any of the schemas available in the **Repo DB**.
*   **Extended Traceability:** Use the `logtime` column to perform advanced trend analysis across different environments and time periods.

> **Note:** When writing custom queries, always remember that the schema name follows the `${compartment}#${display_name}` format. This ensures your dashboard remains dynamic as you switch between targets.

Given the following query:
```sql
SELECT 
    (1 - (SUM(IF(VARIABLE_NAME = 'Innodb_buffer_pool_reads', VARIABLE_VALUE, 0)) / 
    SUM(IF(VARIABLE_NAME = 'Innodb_buffer_pool_read_requests', VARIABLE_VALUE, 1)))) * 100 AS hit_ratio
FROM 
    `${compartment}#${display_name}`.global_status
WHERE 
    VARIABLE_NAME IN ('Innodb_buffer_pool_read_requests', 'Innodb_buffer_pool_reads') 
    AND logtime > NOW() - INTERVAL 1 HOUR;
```
This query processes data from the **last 1 hour** of the `${compartment}#${display_name}.global_status` table. It dynamically targets the specific instance using the `${compartment}` and `${display_name}` dashboard variables.

#### Exposing Custom Metric Data via monitor_tools schema
It's possible to ingest custom metric data without UI / Control Fleet. <br>
On MySQL target database, create views within the `monitor_tools` to standardize access to the tables:
```sql
CREATE DATABASE IF NOT EXISTS monitor_tools;

GRANT SELECT ON monitor_tools.* to 'grafana'@'%';

CREATE VIEW monitor_tools.your_new_metric_table AS 
SELECT * FROM mysql.your_new_metric_table;

CREATE VIEW monitor_tools.your_new_metric_table AS 
SELECT * FROM mysql.your_new_metric_table;
```
