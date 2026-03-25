# Unified MySQL Monitoring Across HeatWave and On-Prem with Grafana Dashboards

MySQL observability is essential in modern enterprises, whether you run a few critical databases or operate at massive scale. With the right real-time monitoring, teams reduce MTTD/MTTR, avoid cascading failures, and continuously track workload health—CPU, memory, I/O, buffer pool efficiency, session contention, transaction/replication lag, error rates, and query latency.

This Grafana monitoring template helps teams understand how to add practical MySQL observability by extracting advanced signals from each target’s `performance_schema` and `information_schema`, persisting them in a dedicated repository MySQL database (repo DB), and visualizing them through actionable Grafana dashboards. Beyond the out-of-the-box views, it also provides a foundation teams can extend to build custom, application-specific observability for their own workloads.

* **Designed for simple, fast deployment, and secure:** A few minutes installation using one command install brings up the full stack (Grafana, repo DB, dispatchers and collector workers) with minimal manual configuration.
* **Built for production use:** It offers low-friction adoption and supports Day 2 monitoring and troubleshooting, remaining extensible across OCI and on-prem environments.
* **Fleet control + flexible scheduling:** A control fleet dashboard registers MySQL targets and manages `performance_schema` collection policies (enable/disable, frequency, collection windows, global table assignments, inclusion/exclusion rules, etc.) to align monitoring depth with each MySQL target’s SLA.

### Features

* **Configuration Monitoring:** Track system variables and configuration changes.
* **Instance Monitoring:** Monitor Uptime, CPU, memory, I/O, and buffer pool efficiency.
* **Security Monitoring:** Audit access patterns and security-related metrics.
* **High Availability Monitoring:** Track replication lag and cluster health.
* **MySQL Enterprise Backup Monitoring:** Monitor backup success and performance.
<br><br>
![MySQL-Monitor Instance](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Fig-1-Grafana%20Dashboard.png)

  


