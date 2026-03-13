# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

variable "terraform_oidc_integration" {
  type = bool
}

variable "terraform_oidc_aws_audience" {
  type = string
}

variable "terraform_oidc_hostname" {
  type = string
}

variable "terraform_project_name" {
  type = string
}

variable "terraform_org_name" {
  type = string
}

variable "terraform_distribution" {
  type = string
}
