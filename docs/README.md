# Unified MySQL Monitoring Across HeatWave and On Prem with Grafana Dashboards

MySQL observability is essential in modern enterprises, whether you run a few critical databases or operate at massive scale. With the right real time monitoring, teams reduce MTTD/MTTR, avoid cascading failures, and continuously track workload health—CPU, memory, I/O, buffer pool efficiency, session contention, transaction/replication lag, error rates, and query latency. </p>
This Grafana monitoring template helps teams understand how to add practical MySQL observability by extracting advanced signals from each target’s performance_schema and information_schema, persisting them in a dedicated repository MySQL database (repo DB), and visualizing them through actionable Grafana dashboards. Beyond the out of the box views, it also provides a foundation teams can extend to build custom, application specific observability for their own workloads </p>
* Designed for simple, fast deployment, and secure: only a few minutes installation using one command install brings up the full stack Grafana, repo DB, dispatchers and collector workers with minimal manual configuration.
* Built for production use, it offers low friction adoption and supports day 2 monitoring and troubleshooting, and remains extensible across OCI and on prem environments.
* Fleet control + flexible scheduling: a control fleet dashboard registers MySQL targets and managed performance_schema collection policies (enable/disable, frequency, collection windows, global table assignments, inclusion/exclusion rules, etc.) to align monitoring depth with each MySQL target’s SLA.


