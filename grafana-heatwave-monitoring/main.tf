terraform {
  required_version =  "> 1.2"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 4.0.0"
    }
  }
}

# provider "oci" {
#   # OCI provider configuration is automatically handled by Resource Manager
# }

# Data source for availability domain
data "oci_identity_availability_domain" "ad" {
  compartment_id = var.tenancy_ocid
  ad_number      = 1
}

# Network
data "oci_core_vcn" "selected_vcn" {
  vcn_id = var.vcn_ocid
}

data "oci_core_subnet" "selected_subnet" {
  subnet_id = var.subnet_ocid
}

# Create the Instance
locals {
  is_flexible_shape = can(regex("Flex$", var.shape))
}
resource "oci_core_instance" "grafana_instance" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  display_name        = var.hostname
  shape               = var.shape

  dynamic "shape_config" {
    for_each = local.is_flexible_shape ? [1] : []
    content {
      ocpus         = var.instance_ocpus
      memory_in_gbs = var.instance_memory_in_gbs
    }
  }


 create_vnic_details {
    subnet_id        = var.subnet_ocid
    assign_public_ip = var.assign_public_ip
    hostname_label   = var.hostname
  }
 source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("./cloud-init.sh"))
  }

  timeouts {
    create = "15m"
  }
}

# Create a Dynamic Group and add instance id
resource "oci_identity_dynamic_group" "grafana_dynamic_group" {
  provider       = oci.home  # Explicitly use the home region provider
  compartment_id = var.tenancy_ocid
  name           = var.dynamic_group_name
  description    = "Dynamic group for Grafana instance"
  matching_rule  = "Any {instance.id = '${oci_core_instance.grafana_instance.id}'}"
}

# Create a Policy
resource "oci_identity_policy" "create_grafana_policy" {
  provider       = oci.home  # Explicitly use the home region provider
  compartment_id = var.tenancy_ocid
  description    = "Grafana Policy Name"
  name           = var.policy_name
  statements     = ["Allow group ${oci_identity_dynamic_group.grafana_dynamic_group.name} to read all-resources in compartment id ocid1.compartment.oc1..aaaaaaaa5oxr4ovmo6kmicilktvyfo5hl3ub6sm5xwxj4oeuiicpgz7zbsaa"]
  }
