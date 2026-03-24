Name:           mysql-monitor
Version:        3.0
Release:        1%{?dist}
Summary:        MySQL monitoring tools and Grafana dashboards

License:        MIT
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

%description
Tools for deploying Grafana dashboards, monitoring MySQL instances, 
and managing HeatWave dashboard configurations.

%prep
%setup -q

%install
# Create target directories
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/home/opc
mkdir -p %{buildroot}/usr/lib/systemd/system

# Install binaries/scripts to /usr/local/bin
install -m 0755 deploy_grafana_dashboard %{buildroot}/usr/local/bin/
install -m 0755 do_monitor.py %{buildroot}/usr/local/bin/
install -m 0755 install_grafana %{buildroot}/usr/local/bin/
install -m 0755 mysql-dispatcher.py %{buildroot}/usr/local/bin/
install -m 0755 mysql-monitor.service %{buildroot}/usr/local/bin/
install -m 0755 mysql-monitor.timer %{buildroot}/usr/local/bin/
install -m 0755 mysql-uptime.py %{buildroot}/usr/local/bin/
install -m 0755 mysql-uptime.service %{buildroot}/usr/local/bin/

# Install config and documentation to /home/opc/
install -m 0644 mysql-global-variable.json %{buildroot}/home/opc/
install -m 0644 mysql-group-replication.json %{buildroot}/home/opc/
install -m 0644 mysql-monitor-configuration.json %{buildroot}/home/opc/
install -m 0644 mysql-monitor-heatwave-dashboard.json %{buildroot}/home/opc/
install -m 0644 mysql-monitor-instance-dashboard.json %{buildroot}/home/opc/
install -m 0644 mysql-monitor-security.json %{buildroot}/home/opc/
install -m 0644 README.txt %{buildroot}/home/opc/

%files
# Executables and systemd files in /usr/local/bin
/usr/local/bin/deploy_grafana_dashboard
/usr/local/bin/do_monitor.py
/usr/local/bin/install_grafana
/usr/local/bin/mysql-dispatcher.py
/usr/local/bin/mysql-monitor.service
/usr/local/bin/mysql-monitor.timer
/usr/local/bin/mysql-uptime.py
/usr/local/bin/mysql-uptime.service

# Config and text files (assigned to opc user)
%attr(0644, opc, opc) /home/opc/mysql-global-variable.json
%attr(0644, opc, opc) /home/opc/mysql-group-replication.json
%attr(0644, opc, opc) /home/opc/mysql-monitor-configuration.json
%attr(0644, opc, opc) /home/opc/mysql-monitor-heatwave-dashboard.json
%attr(0644, opc, opc) /home/opc/mysql-monitor-instance-dashboard.json
%attr(0644, opc, opc) /home/opc/mysql-monitor-security.json
%attr(0644, opc, opc) /home/opc/README.txt

%changelog
* Sun Mar 15 2026 Admin <admin@example.com> - 1.0-1
- Initial build of MySQL monitor tools with dashboards and systemd files.
