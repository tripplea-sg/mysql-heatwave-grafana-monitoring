### MySQL NDB Cluster

MySQL NDB Cluster is the distributed database combining linear scalability and high availability. It provides in-memory real-time access with transactional consistency across partitioned and distributed datasets. It is designed for mission critical applications.
MySQL NDB Cluster has replication between clusters across multiple geographical sites built-in. A shared nothing architecture with data locality awareness make it the perfect choice for running on commodity hardware and in globally distributed cloud infrastructure.

---

#### Implementation Steps

Follow this steps to monitor mysql NDB Cluster from mysql nodes:
**1. Exposing ndbinfo.* Data via monitor_tools schema**
Create views within the `monitor_tools` to standardize access to the audit tables:
```sql
CREATE DATABASE IF NOT EXISTS monitor_tools;

GRANT SELECT ON monitor_tools.* to 'grafana'@'%';

GRANT SHOW VIEW ON monitor_tools.* TO 'grafana'@'%';
```
Sample to expose data node's memory:
```
CREATE VIEW monitor_tools.memoryusage AS 
SELECT * FROM ndbinfo.memoryusage;
```
#### Dashboard Customization
On Grafana query, do the following query to get the ingested data: <br><br>
**Latest NDB Cluster memory usage info:**
```
SELECT * from `${compartment}#${display_name}`.memoryusage
WHERE 
```
