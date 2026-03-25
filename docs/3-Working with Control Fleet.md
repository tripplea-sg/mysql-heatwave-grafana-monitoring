### About Control Fleet
Use the Control Fleet dashboard to register MySQL targets and manage performance_schema collection policies. 
You can toggle metrics globally, define inclusion/exclusion rules for specific targets, and configure advanced scheduling to align monitoring depth with your database SLAs.

#### Accessing Control Fleet
From the left-hand sidebar, navigate to `Dashboards` and select `MySQL-Monitor Control Fleet` from the list.

![oci-data-source](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Control_fleet-1.png)

### 🖥️ Target Management
#### 1. Register or Update a MySQL Target
Configure the connection details for a new database instance as shown in the image above.

*   **Compartment:** The OCI Compartment ID (Cloud) or an environment label like `PROD`, `DEV`, or `TEST` (On-Premise).
*   **Instance:** The MySQL HeatWave display name (Cloud) or a custom descriptive name (On-Premise).
*   **Connection Details:** Provide the **IP Address**, **Port**, **Username**, and **Password** for the target MySQL instance.
*   **Interval (Minutes):** The frequency of metric data collection (e.g., every 1, 5, or 10 minutes).
*   **Retention (Days):** The number of days historical data is stored in the Repository DB before being purged.
*   **Monitoring Window:** Use **Start** and **End Date Time** to define the active monitoring period. 
    *   *Tip: To stop monitoring a target immediately, simply set the **End Date Time** to a past date.*

> **To Update an Existing Target:** Enter the same **Compartment**, **Instance**, and **Connection Details**, then adjust the **Interval**, **Retention**, or **Monitoring Window** as needed. The system will update the existing record based on these identifiers.


#### 2. Manage Global Performance Schema Metrics
Enable or disable specific `performance_schema` collections across your entire fleet.


#### Customizing Instance Metrics
*   **Add Specific Metrics to an Instance:** Enable deeper granularity for high-priority targets.
*   **Exclude Metrics from an Instance:** Reduce noise and overhead for specific environments.

---

### 📊 Repository Health & Optimization
#### Monitor Repository Database Performance
Track the health and resource utilization of the monitoring "Repo DB" itself.

#### Storage Analysis & Capacity Planning
*   **Storage by Target:** Identify which MySQL targets are consuming the most space in the repository.
*   **Storage by Table:** Audit which `performance_schema` tables are driving repository growth.

#### Query Optimization
*   **Slow Query Analysis:** Identify and troubleshoot latent queries within the repository database.

