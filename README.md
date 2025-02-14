# Let's Encrypt TLS Certificate Automation

🔒 Automate Let's Encrypt SSL/TLS certificate creation and renewal using GitHub Actions, with support for cross-account AWS Route53 DNS validation.

## Features

- Create or renew Let's Encrypt certificates
- Support for both DNS and HTTP validation methods
- Cross-account AWS support (separate DNS and application accounts)
- Automatic certificate upload to target servers
- CloudFormation templates for AWS setup
- Comprehensive error handling

## Quick Start

1. Deploy CloudFormation templates to both AWS accounts
2. Configure GitHub repository secrets
3. Set up the GitHub Actions workflow
4. Run the workflow with your desired configuration

## AWS Account Setup

### DNS Account (Route53)
Deploy the CloudFormation template:
```bash
aws cloudformation create-stack \
  --stack-name certbot-dns-role \
  --template-body file://dns-account.yml \
  --parameters \
    ParameterKey=AppAccountId,ParameterValue=YOUR_APP_ACCOUNT_ID \
    ParameterKey=ExternalId,ParameterValue=YOUR_EXTERNAL_ID \
  --capabilities CAPABILITY_NAMED_IAM
```

### App Account
Deploy the CloudFormation template:
```bash
aws cloudformation create-stack \
  --stack-name certbot-app-role \
  --template-body file://app-account.yml \
  --parameters \
    ParameterKey=DNSAccountId,ParameterValue=YOUR_DNS_ACCOUNT_ID \
    ParameterKey=GitHubOrg,ParameterValue=YOUR_GITHUB_ORG \
    ParameterKey=GitHubRepo,ParameterValue=YOUR_GITHUB_REPO \
    ParameterKey=CertificateBucketName,ParameterValue=YOUR_BUCKET_NAME \
  --capabilities CAPABILITY_NAMED_IAM
```

## GitHub Setup

1. Add required secrets:
   ```
   AWS_DNS_ACCOUNT_ID
   AWS_APP_ACCOUNT_ID
   AWS_DNS_ROLE_NAME
   AWS_APP_ROLE_NAME
   AWS_REGION
   AWS_EXTERNAL_ID
   SSH_PRIVATE_KEY (if using remote upload)
   ```

2. Configure workflow inputs:
   ```json
   // DNS validation
   {
     "action": "create",
     "domain": "example.com",
     "email": "admin@example.com",
     "verification_method": "dns",
     "target_config": {
       "hosted_zone_id": "Z0123456789ABCDEF"
     },
     "environment": "production",
     "upload_target": {
       "host": "server.example.com",
       "user": "admin",
       "path": "/etc/ssl/private"
     }
   }
   ```

   ```json
   // HTTP validation
   {
     "action": "create",
     "domain": "example.com",
     "email": "admin@example.com",
     "verification_method": "http",
     "target_config": {
       "webroot_path": "/var/www/html"
     },
     "environment": "production"
   }
   ```

## Running the Workflow

1. Go to Actions tab in your repository
2. Select "Let's Encrypt Certificate Setup"
3. Click "Run workflow"
4. Fill in the required parameters
5. Certificates will be generated and optionally uploaded

## Troubleshooting

Common issues and solutions:

1. Cross-Account Access
   - Verify IAM role trust relationships
   - Check external ID configuration
   - Ensure proper Route53 permissions

2. DNS Validation
   - Verify hosted zone ID
   - Check DNS propagation
   - Confirm Route53 access

3. HTTP Validation
   - Verify webroot path exists
   - Check web server configuration
   - Confirm ACME challenge accessibility

## File Structure
```
.
├── .github
│   └── workflows
│       └── letsencrypt-setup.yml
├── cloudformation
│   ├── dns-account.yml
│   └── app-account.yml
├── scripts
│   ├── setup_certificate.py
│   └── cross_account_handler.py
└── README.md
```

## Contributions

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Related Projects

This project is available at [icsi-it/cert-renewal](https://github.com/icsi-it/cert-renewal) - the official ICSI IT repository for certificate automation.

## License

This project is licensed under the MIT License.