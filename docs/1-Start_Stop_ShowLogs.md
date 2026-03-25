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


