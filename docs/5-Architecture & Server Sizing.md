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




