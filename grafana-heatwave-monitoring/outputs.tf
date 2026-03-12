output "instance_id" {
  description = "OCID of created instance"
  value       = oci_core_instance.grafana_instance.id
}

output "public_ip" {
  description = "Public IP address of instance"
  value       = oci_core_instance.grafana_instance.public_ip
}

output "private_ip" {
  description = "Private IP address of instance"
  value       = oci_core_instance.grafana_instance.private_ip
}