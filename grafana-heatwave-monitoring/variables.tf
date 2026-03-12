variable "compartment_ocid" {
  description = "The OCID of the compartment where resources will be created"
  type        = string
}

variable "availability_domain" {
  description = "The name of the availability domain"
  type        = string
}

variable "vcn_ocid" {
  description = "The OCID of the VCN"
  type        = string
}

variable "subnet_ocid" {
  description = "The OCID of the subnet"
  type        = string
}

variable "tenancy_ocid" {
  description = "The OCID of the tenancy"
  type        = string
}

variable "region" {
  description = "The OCI region"
  type        = string
}

variable "hostname" {
  description = "The hostname of the Instance"
  type        = string
}

variable "image_ocid" {
  description = "The OCID of the image to use for the instance"
  type        = string
}

# variable "image_ocid" {
#   description = "The OCID of the image to use for the instance"
#   type        = string
#   default = {
#     "us-ashburn-1" = "ocid1.image.oc1.iad.aaaaaaaaxtzkhdlxbktlkhiausqz7quag7d5jqbrgy6empmrojtdktwfv7fq"
#     "us-phoenix-1" = "ocid1.image.oc1.phx.aaaaaaaaoqj42sokaoh42l76wsyhn3k2beuntrh5maj3gmgmzeyr55zzrwwa"
#   }
# }

variable "shape" {
  description = "The shape of the instance"
  type        = string
  default     = "VM.Standard2.1"
}

# variable "available_shapes" {
#   description = "List of available shapes"
#   type = list(string)
#   default = ["VM.Standard2.1", "VM.Standard1.1", "VM.Standard1.8", "VM.Standard.E4.Flex", "VM.Standard.E3.Flex"]
# }

variable "instance_ocpus" {
  description = "Number of OCPUs for flexible shapes"
  type        = number
  default     = 1
}

variable "instance_memory_in_gbs" {
  description = "Amount of memory in GBs for flexible shapes"
  type        = number
  default     = 16
}


variable "assign_public_ip" {
  description = "Whether to assign a public IP to the instance"
  type        = bool
  default     = true
}

variable "ssh_public_key" {
  description = "The SSH public key to use for the instance"
  type        = string
}

variable "dynamic_group_name" {
  description = "Create a Dynamic Group and add instance id"
  type        = string
}

variable "policy_name" {
  description = "Create a Policy Name"
  type        = string
}
