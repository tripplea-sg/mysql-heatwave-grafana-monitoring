### About Control Fleet
Use the Control Fleet dashboard to register MySQL targets and manage performance_schema collection policies. 
You can toggle metrics globally, define inclusion/exclusion rules for specific targets, and configure advanced scheduling to align monitoring depth with your database SLAs.

#### Accessing Control Fleet
From the left-hand sidebar, navigate to `Dashboards` and select `MySQL-Monitor Control Fleet` from the list.

![oci-data-source](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Control_fleet-1.png)

### 🖥️ Target Management
#### Register a New MySQL Target
Add and configure connection details for a new database instance.

#### Manage Global Performance Schema Metrics
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

