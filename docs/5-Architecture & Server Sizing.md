### Database Repository Structure
Every MySQL target is mapped to a dedicated schema in the Repository Database (repo DB) using the following naming convention:
**`<Compartment_Name>_<Instance_Name>`**

To ensure familiarity and ease of use, the system creates a corresponding table for every collected `performance_schema` table within each target's schema.

**Key features of the table structure:**
*   **Identical Schema:** Tables mirror the source structure of the MySQL target for seamless query transition.
*   **Invisible Timestamp:** Each table is augmented with a `logtime` column, which stores the timestamp of collection based on the **repo DB clock**.
*   **Traceability:** The `logtime` column is defined as **INVISIBLE**. This preserves compatibility with the original source table structure while enabling powerful chronological filtering and time-series trending in Grafana.

### 💡 Usability & Purpose
1.  **Historical Analysis:** Move beyond real-time snapshots to see how performance metrics evolve over days or weeks.
2.  **Schema Isolation:** Dedicated schemas prevent data collision between different environments (e.g., PROD vs. DEV).
3.  **Grafana Integration:** The `logtime` column acts as the primary time-series axis for all monitoring dashboards.

![MySQL-Monitor Instance](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Data_Architecture.png)

#### 🛠️ Custom Query Example: InnoDB Buffer Pool Hit Ratio

The following example demonstrates how to retrieve and visualize the latest **InnoDB Buffer Pool Hit Ratio** from the repository database. This query utilizes Grafana dashboard variables—`${compartment}` (OCI Compartment) and `${display_name}` (MySQL HeatWave Name)—to dynamically target the correct schema.

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

---
### Monitoring Architecture Overview
The following architecture components are installed and running in the server automatically during installation.

![MySQL-Monitor Instance](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Components.png)

This template utilizes a centralized data plane rather than individual data sources for each MySQL target. This approach keeps the Grafana configuration simple, consistent, and scalable.

#### 1. Data Collection Orchestration
The collection process is managed by **systemd-based scheduling**, which executes the dispatcher script every minute.

*   **Dispatcher Script:** `/usr/local/bin/mysql-dispatcher.py`
*   **Systemd Units:**
    *   `/usr/lib/systemd/system/mysql-monitor.service`
    *   `/usr/lib/systemd/system/mysql-monitor.timer`

The dispatcher triggers **collector workers** (`/usr/local/bin/do-monitor.py`) for each MySQL target. These workers query the `performance_schema` and write the results into the repository database.

#### 2. Uptime Monitoring
Uptime is tracked by a separate scheduler process to ensure high-frequency health checks.

*   **Execution Script:** `/usr/local/bin/mysql-uptime.py`
*   **Systemd Service:** `mysql-uptime.service`
*   **Frequency:** Every 10 seconds.
*   **Data Format:** Stores status as `1` (Up) or `0` (Down) in the repository database.





