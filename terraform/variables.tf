variable "project_id" {
  type = string
  description = "The ID of the Google Cloud project"
}

variable "region" {
  type = string
  description = "The region to deploy to"
  default = "us-central1"
}

# variable "service_account_key_file" {
#   type = string
#   description = "Path to the service account key file"
# }

variable "tf_state_bucket" {
  type = string
  description = "The name of the GCS bucket to store Terraform state"
}

variable "cloud_run_service_account" {
  type = string
  description = "The email address of the Cloud Run service account"
}

# Add more variables as needed
