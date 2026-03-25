# Operation
### Start-Up Procedure
Start MySQL repository database instance if not up:
```bash
sudo systemctl start mysqld
```

Start Grafana server if not up:
```bash
sudo systemctl start grafana-server
```
Start Monitoring if not up:
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

