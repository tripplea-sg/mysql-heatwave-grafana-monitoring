### 1. MySQL-Monitor Database Global Variables
The **Global Variables** view is essential for maintaining a healthy monitoring fleet:

1. **Policy Verification:** Quickly confirm that a specific target is correctly inheriting global defaults for collection frequency and data retention.
2. **Conflict Resolution:** Easily identify if an instance is following the **Global Policy** or if a **Local Override** (Target-specific setting) is currently active.

> **Note:** If the `variable_value` differs from your global defaults, it indicates that a manual override has been applied to that specific MySQL target in the **Instance Metrics** section.

---

### 2. MySQL-Monitor Group Replication
Monitoring **Group Replication** variables is critical for maintaining database availability:

1. **Failover Awareness:** Instantly identify which node is the current **Primary** and ensure that writes are being directed correctly.
2. **Health Tracking:** Monitor the `member_state` to catch nodes in a `RECOVERING` or `OFFLINE` state before they impact application performance.
3. **Data Consistency:** Use `replication_lag` to verify that secondary nodes are up-to-date, ensuring minimal **RPO (Recovery Point Objective)** during a failover.

> **Tip:** If a node shows as `OFFLINE`, check the **Security Monitoring** section to verify if network communication between cluster members is being blocked.

---

### 3. MySQL-Monitor HeatWave
This section provides a unified observability view by combining internal database metrics with infrastructure-level health data.

**Data Sources & Architecture:**
To provide 360-degree visibility, this dashboard pulls data from two distinct sources:
1.  **MySQL Performance Schema:** Collected directly from the `performance_schema` of your **MySQL target**. This provides granular SQL-level diagnostics, statement latency, and internal engine statistics.
2.  **OCI Monitoring Service:** Ingested via the **OCI Monitoring Metrics** API. This delivers infrastructure health data such as HeatWave Cluster CPU/Memory utilization, network throughput, and disk I/O.

Combining these sources allows for comprehensive troubleshooting of HeatWave workloads:

1.  **Metric Correlation:** Match a spike in **OCI CPU utilization** directly to a specific slow query identified via the **Performance Schema**.
2.  **Capacity Planning:** Use OCI infrastructure metrics to determine if your **HeatWave Cluster** shape needs to be upsized for your analytical dataset.
3.  **Proactive Health Checks:** Monitor the cluster state alongside database internals to ensure high availability and optimal performance.

> **Note:** Ensure your **OCI Data Source** is correctly configured with the necessary IAM policies to allow Grafana to read OCI Monitoring metrics.


