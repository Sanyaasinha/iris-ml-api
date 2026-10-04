#!/usr/bin/env bash
# One-time setup on a fresh Amazon Linux 2023 EC2 instance.
set -e
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
# AWS CLI v2 is preinstalled on Amazon Linux 2023
echo "Done. Log out and back in so the docker group takes effect."
