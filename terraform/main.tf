terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = var.tf_state_bucket
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
    auto {}
  }
}

resource "google_service_account" "discord_cloudrun_account" {
  account_id   = "cloud-run-discord-sa"
  description  = "Identity used by the discord service to call private Cloud Run services."
  display_name = "cloud-run-discord-sa"
}

resource "google_cloud_run_v2_service" "mealbot_discord_bot_service" {
  name     = "mealbot-discord-bot"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = var.cloud_run_discord_image_uri
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "API_BASE_URL"
        value = google_cloud_run_v2_service.mealbot_api_service.uri
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
    service_account = google_service_account.discord_cloudrun_account.email
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

data "google_iam_policy" "discord_public_iam" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "discord_public_iam" {
  location = google_cloud_run_v2_service.mealbot_discord_bot_service.location
  project  = google_cloud_run_v2_service.mealbot_discord_bot_service.project
  service  = google_cloud_run_v2_service.mealbot_discord_bot_service.name

  policy_data = data.google_iam_policy.discord_public_iam.policy_data
}


resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.discord_token_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.discord_cloudrun_account.email}"
}

resource "google_cloud_run_v2_service" "mealbot_api_service" {
  name     = "mealbot-api"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = var.cloud_run_api_image_uri
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      resources {
        limits = {
          memory = "1Gi"
          cpu    = "2"
        }
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_service_iam_member" "api_invoker_permission" {
  service  = google_cloud_run_v2_service.mealbot_api_service.name
  location = google_cloud_run_v2_service.mealbot_api_service.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.discord_cloudrun_account.email}"
}
