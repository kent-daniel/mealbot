variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}

variable "region" {
  type        = string
  description = "The region to deploy to"
  default     = "us-central1"
}

variable "tf_state_bucket" {
  type        = string
  description = "The name of the GCS bucket to store Terraform state"
}

variable "cloud_run_service_account" {
  type        = string
  description = "The email address of the Cloud Run service account"
}

variable "cloud_run_discord_image_uri" {
  type        = string
  description = "container image uri for discord bot cloud run service"
}

variable "cloud_run_api_image_uri" {
  type        = string
  description = "container image uri for api cloud run service"
}
