### Data Architecture
Grafana is highly customizable: the existing template can be customized and new dashboards can be built largely in the UI with little to no coding. However, for panels that read from the repo DB, it’s important to understand the schema and data model produced by the collectors before making modification or build a new dashboard. See the following illustration. <br>
![MySQL-Monitor Instance](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Data_Architecture.png)

Every MySQL target is mapped to its own dedicated schema in the repo DB. Naming convention for database schema is as follow:

