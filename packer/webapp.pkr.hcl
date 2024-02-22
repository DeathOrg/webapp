packer {
  required_plugins {
    googlecompute = {
      version = ">= 1.1.4"
      source  = "github.com/hashicorp/googlecompute"
    }
  }
}

variable "gcp_project_id" {
  type      = string
  default   = ""
  sensitive = true
}

variable "source_image_family" {
  type    = string
  default = "centos-stream-8"
}

variable "ssh_username" {
  type    = string
  default = "csye6225"
}

variable "ssh_user_group" {
  type    = string
  default = "csye6225"
}

variable "zone" {
  type    = string
  default = "us-central1-b"
}

variable "image_family" {
  type    = string
  default = "my-webapp"
}

variable "disk_type" {
  type    = string
  default = "pd-balanced"
}

variable "disk_size" {
  type    = string
  default = "20"
}

variable "app_artifact_path" {
  type    = string
  default = "../app_artifact/webapp.zip"
  #  default = "/Users/sourabhkumar/Downloads/webapp.zip"
}

variable "requirement_path" {
  type = string
  #  default = "../app_artifact/webapp.zip"
  default = "requirements/requirements.txt"
  #  default = "/Users/sourabhkumar/Documents/NEU/Sem-2/Cloud/Assignments/Assignment-02/webapp/packer/scripts/requirements.txt"
}

variable "mysql_root_password" {
  type      = string
  sensitive = true
}

variable "mysql_database_name" {
  type    = string
  default = "webApp"
}

variable "mysql_user" {
  type    = string
  default = "dev-1"
}

variable "mysql_user_password" {
  type      = string
  sensitive = true
}


source "googlecompute" "webapp" {
  project_id          = var.gcp_project_id
  source_image_family = var.source_image_family
  ssh_username        = var.ssh_username
  zone                = var.zone
  image_name          = "${var.image_family}-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  image_family        = var.image_family

  disk_type = var.disk_type
  disk_size = var.disk_size
}

build {
  sources = [
    "source.googlecompute.webapp"
  ]

  provisioner "shell" {
    script = "scripts/create_user.sh"
  }

  # Copy application artifacts and configuration
  provisioner "file" {
    source      = var.requirement_path
    destination = "/tmp/requirements.txt"
  }

  # Install dependencies
  provisioner "shell" {
    script = "scripts/install_dependencies.sh"
  }

  # Copy application artifacts and configuration
  provisioner "file" {
    source      = var.app_artifact_path
    destination = "/home/${var.ssh_username}/webapp.zip"
  }

  # Unzip and set permissions
  provisioner "shell" {
    inline = [
      "cd /home/csye6225",
      "unzip webapp.zip",
      "chown -R csye6225:csye6225 *"
    ]
  }

  provisioner "file" {
    source      = "./webapp.service"
    destination = "/tmp/webapp.service"
  }

  provisioner "shell" {
    script = "scripts/app_start_up.sh"
    environment_vars = [
      "MYSQL_ROOT_PASSWORD=${var.mysql_root_password}",
      "DATABASE_NAME=${var.mysql_database_name}",
      "DATABASE_USER=${var.mysql_user}",
      "DATABASE_PASSWORD=${var.mysql_user_password}",
      "MY_DB=${var.mysql_user_password}"
    ]
  }
}
