{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:${data_aws_partition_current_partition}:iam::${aft_account_id}:root"
      },
      "Action": "sts:AssumeRole"
    }

    %{ if oidc_provider_arn != "" }
    ,{
      "Effect": "Allow",
      "Principal": {
        "Federated": "${oidc_provider_arn}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${terraform_oidc_hostname}:aud": "${terraform_oidc_aws_audience}"
        },
        "StringLike": {
          "${terraform_oidc_hostname}:sub": "organization:${terraform_org_name}:project:${terraform_project_name}:workspace:*:run_phase:*"
        }
      }
    }
    %{ endif }
  ]
}
