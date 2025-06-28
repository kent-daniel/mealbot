terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "${var.tf_state_bucket}"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_secret_manager_secret" "discord_token_secret" {
  secret_id = "discord-token"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "discord_token_version" {
  secret = google_secret_manager_secret.discord_token_secret.id
  secret_data = var.discord_token
}

resource "google_cloud_run_v2_service" "default" {
  name     = "mealbot-discord-bot"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "gcr.io/${var.project_id}/mealbot-discord-bot"
      env {
        name  = "DISCORD_TOKEN"
        value = google_secret_manager_secret_version.discord_token_version.secret_data
      }
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }
    
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id   = google_secret_manager_secret.discord_token_secret.id
  role     = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${var.cloud_run_service_account}"
}
