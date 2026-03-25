### Data Architecture
Grafana is highly customizable: the existing template can be customized and new dashboards can be built largely in the UI with little to no coding. However, for panels that read from the repo DB, it’s important to understand the schema and data model produced by the collectors before making modification or build a new dashboard. See the following illustration. <br>
![MySQL-Monitor Instance](https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/blob/main/docs/images/Data_Architecture.png)

Every MySQL target is mapped to its own dedicated schema in the repo DB with the following naming convention: <br><br>

Every collected performance tables, the system creates a corresponding table with same name under every target’s schemas, preserving a similar structure for familiarity. To support traceability and time-series visualization, each table is augmented with `logtime` invisible column that stores  `timestamp` when record was collected; using `repo DB` time clock. The `logtime` is an INVISIBLE column to preserve consistency with source table structure in MySQL targets while enabling chronological filtering and trending in Grafana.


