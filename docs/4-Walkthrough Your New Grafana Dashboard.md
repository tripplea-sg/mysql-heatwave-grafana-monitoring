#### MySQL-Monitor Database Global Variables
The **Global Variables** view is essential for maintaining a healthy monitoring fleet:

1. **Policy Verification:** Quickly confirm that a specific target is correctly inheriting global defaults for collection frequency and data retention.
2. **Conflict Resolution:** Easily identify if an instance is following the **Global Policy** or if a **Local Override** (Target-specific setting) is currently active.

> **Note:** If the `variable_value` differs from your global defaults, it indicates that a manual override has been applied to that specific MySQL target in the **Instance Metrics** section.

---

#### MySQL-Monitor Group Replication
Monitoring **Group Replication** variables is critical for maintaining database availability:

1. **Failover Awareness:** Instantly identify which node is the current **Primary** and ensure that writes are being directed correctly.
2. **Health Tracking:** Monitor the `member_state` to catch nodes in a `RECOVERING` or `OFFLINE` state before they impact application performance.
3. **Data Consistency:** Use `replication_lag` to verify that secondary nodes are up-to-date, ensuring minimal **RPO (Recovery Point Objective)** during a failover.

> **Tip:** If a node shows as `OFFLINE`, check the **Security Monitoring** section to verify if network communication between cluster members is being blocked.




