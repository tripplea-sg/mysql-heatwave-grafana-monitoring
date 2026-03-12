#!/bin/bash

set -ex
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting Grafana installation script"
# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

echo "Installing Grafana..."
if ! yum install -y https://dl.grafana.com/enterprise/release/grafana-enterprise-11.1.0-1.x86_64.rpm; then
    echo "Failed to install Grafana" >&2
    exit 1
fi
echo "Grafana installation completed"

echo "Reloading systemd..."
systemctl daemon-reload
echo "Systemd reload completed"

echo "Starting Grafana server..."
if ! systemctl start grafana-server; then
    echo "Failed to start Grafana server" >&2
    systemctl status grafana-server
    exit 1
fi
echo "Grafana server started"

echo "Enabling Grafana to start on boot..."
systemctl enable grafana-server
systemctl enable grafana-server.service
echo "Grafana installation and setup completed successfully"

echo "Installing oci-metrics-datasource..."
grafana-cli plugins install oci-metrics-datasource
echo "Plugin installed"

echo "Changing ownership of plugins..."
sudo chown -R grafana:grafana /var/lib/grafana/plugins
echo "Ownership changed"

# echo "Updating grafana.ini to allow unsigned plugins..."
# echo "allow_loading_unsigned_plugins = oci-metrics-datasource" | tee -a /etc/grafana/grafana.ini
# echo "grafana.ini updated"

echo "Restarting Grafana server..."
systemctl restart grafana-server
echo "Grafana server restarted"

# echo "Check current SELinux mode ..."
current_mode=$(getenforce)
# echo "Current SELinux mode: $current_mode"

# echo "Setting SELinux to permissive mode..."
setenforce 0

echo "Opening port 3000 in the firewall..."
firewall-cmd --zone=public --add-port=3000/tcp --permanent
firewall-cmd --reload

# Set SELinux back to its original mode
echo "Setting SELinux back to $current_mode mode..."
if [ "$current_mode" = "Enforcing" ]; then
    setenforce 1
fi

# echo "Verifying port 3000 is open..."
# firewall-cmd --zone=public --list-ports

# Check SELinux status
echo "Current SELinux mode: $(getenforce)"

echo "Checking Grafana server status:"
systemctl status grafana-server
echo "Installation and configuration completed"
