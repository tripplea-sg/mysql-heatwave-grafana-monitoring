provider "oci" {
  alias        = "current"
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
}

data "oci_identity_region_subscriptions" "this" {
  tenancy_id = var.tenancy_ocid
}

provider "oci" {
  alias        = "home"
  tenancy_ocid = var.tenancy_ocid
  region       = "us-ashburn-1"
}
