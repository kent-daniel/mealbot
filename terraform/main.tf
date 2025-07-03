terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "terraform-state-mealbot777"
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

resource "google_cloud_run_v2_service" "default" {
  name     = "mealbot-discord-bot"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "gcr.io/${var.project_id}/mealbot-discord-bot"
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }
    service_account = var.cloud_run_service_account
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
