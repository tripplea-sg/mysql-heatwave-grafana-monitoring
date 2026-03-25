# Installation

### Pre-Requisites on OCI Instance
If you are on OCI, provision a compute instance with **Oracle Linux 9**. Please refer to the official documentation on [how to create an OCI Compute instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm).

---

### Pre-Requisites on VM/Bare Metal
If you are not on OCI, provision a server (VM or Bare Metal) with **Oracle Linux 9** or **Red Hat Enterprise Linux 9**.

Login to your server as the `root` user and create the `opc` user:

**1. Create `opc` user**
```bash
sudo groupadd opc
sudo useradd -m -d /home/opc -g opc -s /bin/bash opc
```

**2. Grant password less sudo privileges by creating a dedicated sudoers file**
```bash
echo "opc ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/opc
sudo chmod 0440 /etc/sudoers.d/opc
sudo passwd opc
```

### Pre-requisites on MySQL target
Create (if not exists) database user for monitoring and ensure it has SELECT privileges on performance_schema and mysql.component schema.
```
MySQL > CREATE USER <user>@’%’ IDENTIFIED BY ‘<complex_password>’;
MySQL > GRANT SELECT on performance_schema.* to <user>@’%’;
MySQL > GRANT SELECT on mysql.component to <user>@’@’;
```

### Installation Steps
It takes less than 15 minutes to complete the whole thing here. Just login to your grafana server and install: 

**1. Install tools**
```bash
sudo yum install -y sudo yum install -y https://github.com/tripplea-sg/mysql-heatwave-grafana-monitoring/raw/main/releases/mysql-monitor-3.0-1.el9.noarch.rpm
```

**2. Setup Instance**
```
install_grafana
```
Set your new password for `root@localhost` of MySQL repository database and admin user for Grafana.

**3. Install dashboard**





