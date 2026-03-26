Grafana Monitoring Suite
========================

Overview
--------
This project is a lightweight Grafana-based monitoring solution designed and developed to provide visibility into MySQL environments, including HeatWave deployments.

It delivers real-time insights and performance analytics using MySQL as the backend repository. The solution is designed for simplicity, operating entirely on a single server without external dependencies such as Prometheus.


Features
--------

1. MySQL Monitoring
- Real-time performance metrics
- Query performance insights
- Resource utilization tracking (CPU, memory, I/O)
- Slow query analysis
- Connection monitoring

2. HeatWave Monitoring
- Cluster performance visibility
- Query acceleration tracking
- HeatWave node health monitoring
- Workload distribution insights

3. Uptime Monitoring
- Instance availability tracking
- Downtime logging
- SLA reporting support

4. Instance Monitoring
- Detailed per-instance dashboards
- Resource usage breakdown

5. High Availability and Replication
- Replication status monitoring
- Replication lag visibility
- Failover readiness visibility
- Multi-node synchronization tracking

6. Security Monitoring
- Unauthorized access visibility
- Login activity tracking
- Privilege change monitoring
- Audit log visualization

7. Advanced Scheduling
- Custom data collection intervals
- Scheduled reporting
- Dashboard refresh configuration


Architecture
------------
The monitoring stack is designed for single-server deployment:

- Grafana for visualization
- MySQL as the central metrics repository
- Python scripts and queries for data collection


Server Installation
-------------------

Run the following commands to install and deploy the monitoring suite:

$ sudo yum install -y https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/raw/main/releases/mysql-monitor-3.1-1.el9.noarch.rpm

$ install_grafana

$ deploy_grafana_dashboard


MySQL Target Installation
-------------------------
MySQL database user for database connection with the following privileges:
- SELECT on performance_schema.*
- SELECT on mysql.component

Syntax:
GRANT SELECT on performance_schema.* to <your_monitoring_user>@'%';
GRANT SELECT on mysql.component to <your_monitoring_user>@'%';


Usage
-----
- Access dashboards through Grafana UI
- Configure MySQL data source
- Customize panels based on your environment
- Monitor system health and performance in real time


Requirements
------------
- Oracle Linux 9 / RedHat Enterprise Linux 9
- Grafana (latest stable version recommended)
- MySQL / HeatWave instance (used as repository)
- Single server environment (recommended)
- Network access to monitored MySQL instances


License
-------
This project is licensed under the GNU General Public License v3.0 (GPL v3).

You are free to use, modify, and distribute this software under the terms of the GPL v3 license.


Author
------
Developed by: Hananto Wicaksono


Contributions
-------------
Contributions, suggestions, and improvements are welcome.
Please submit issues or pull requests where applicable.


Disclaimer
----------
This project is provided "as is" without warranty of any kind.
Use at your own risk in production environments.
