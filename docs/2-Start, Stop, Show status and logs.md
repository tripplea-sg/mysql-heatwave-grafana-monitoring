# Operation
### Start Monitoring Services
Start MySQL repository database instance if not up:
```bash
sudo systemctl start mysqld
```

Start Grafana server if not up:
```bash
sudo systemctl start grafana-server
```
Start Monitoring Processes if not up:
```bash
sudo systemctl start mysql-monitor.timer
sudo systemctl start mysql-uptime.service
```

### Show Status and Logs
Check status of every components and they shall show active or disabled:
**1. On database:**
```bash
sudo systemctl status mysqld
```
**2. On Grafana:**
```bash
sudo systemctl status grafana-server
```
**3. On Monitoring service:**
```bash
sudo systemctl status mysql-monitor.timer
sudo systemctl status mysql-uptime.service
```
To check the logs for error or progress by showing last 50 records, issue the following command
```bash
journalctl -u mysql-monitor.service -n 50 -f
journalctl -u mysql-uptime.service -n 50 -f 
```

### Stop Monitoring Services
Stop Monitoring Processes:
```bash
sudo systemctl stop mysql-monitor.timer
sudo systemctl stop mysql-uptime.service
```

Stop Grafana server if not up:
```bash
sudo systemctl stop grafana-server
```
Stop MySQL repository database instance if not up:
```bash
sudo systemctl stop mysqld
```
