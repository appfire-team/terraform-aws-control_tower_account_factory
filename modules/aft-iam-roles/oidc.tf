# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# Create provider configuration when HCP OIDC integration is enabled

data "tls_certificate" "hcp_terraform" {
  count = local.enable_oidc ? 1 : 0
  url   = "https://${var.terraform_oidc_hostname}"
}

resource "aws_iam_openid_connect_provider" "hcp_terraform" {
  count    = local.enable_oidc ? 1 : 0
  provider = aws.aft_management

  url             = data.tls_certificate.hcp_terraform[0].url
  client_id_list  = [var.terraform_oidc_aws_audience]
  thumbprint_list = [data.tls_certificate.hcp_terraform[0].certificates[0].sha1_fingerprint]
}
