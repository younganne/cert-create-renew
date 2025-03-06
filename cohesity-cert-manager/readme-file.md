# Cohesity Certificate Management Solution

This project provides an automated solution for managing Let's Encrypt SSL certificates for Cohesity clusters.

## Overview

The solution uses Docker to create an isolated environment that:
1. Obtains and renews Let's Encrypt certificates
2. Automatically deploys renewed certificates to a Cohesity cluster
3. Provides logging and monitoring for the certificate management process

## Prerequisites

- Docker and Docker Compose installed on the host system
- Network access to Let's Encrypt servers (port 80/443)
- SSH access to the Cohesity cluster (for SSH-based deployment)
- API access to the Cohesity cluster (for API-based deployment)

## Project Structure

```
.
├── Dockerfile               # Container definition
├── docker-compose.yml       # Container orchestration
├── scripts/
│   ├── entrypoint.sh        # Container entrypoint script
│   ├── cert_renewal.sh      # Certificate renewal script
│   ├── deploy_cert.py       # API-based deployment script
├── ssh/
│   └── ssh_key              # SSH private key for deployment (you must provide this)
├── letsencrypt/             # Mounted volume for certificate storage
└── logs/                    # Mounted volume for logs
```

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/cohesity-cert-manager.git
   cd cohesity-cert-manager
   ```

2. **Prepare SSH key (if using SSH-based deployment)**

   ```bash
   # Generate a new key pair
   ssh-keygen -t rsa -b 4096 -f ssh/ssh_key -N ""
   
   # Add the public key to the Cohesity cluster
   # You'll need to follow Cohesity's documentation for adding the public key
   ```

3. **Set up Docker Secrets**

   ```bash
   # Create a secrets directory
   mkdir -p secrets
   
   # Create the password secret file
   echo "your-secure-password" > secrets/cohesity_password.txt
   
   # Secure the secrets file
   chmod 600 secrets/cohesity_password.txt
   ```

4. **Configure environment variables**

   ```bash
   # Create a .env file for non-sensitive environment variables
   cp .env.example .env
   
   # Edit the .env file with your specific settings
   nano .env
   ```

4. **Build and start the container**

   ```bash
   docker-compose up -d
   ```

5. **Verify the initial certificate request**

   ```bash
   docker-compose logs -f
   ```

## Configuration Options

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DOMAIN | Domain for the certificate | malkovich.sys.icsi.berkeley.edu |
| EMAIL | Contact email for Let's Encrypt | admin@example.com |
| COHESITY_HOST | Hostname of the Cohesity cluster | malkovich.sys.icsi.berkeley.edu |
| COHESITY_USER | Admin username for the Cohesity cluster | admin |
| COHESITY_PASSWORD | Admin password for the Cohesity cluster | password123 |
| DEPLOY_METHOD | Deployment method (ssh or api) | ssh |

### Deployment Methods

1. **SSH Method**
   - Uses SSH to copy the certificate to the Cohesity cluster
   - Executes the Cohesity CLI command to install the certificate
   - Requires SSH key authentication to be set up

2. **API Method**
   - Uses the Cohesity REST API to upload and install the certificate
   - Requires admin credentials
   - More secure as it doesn't require SSH access

## Maintenance

### Logs

Logs are stored in the mounted `logs` directory. You can view them with:

```bash
tail -f logs/cron.log
```

### Certificate Renewal

Certificates are automatically renewed when they're 30 days from expiration. You can trigger a manual renewal with:

```bash
docker exec cohesity-cert-manager certbot renew --force-renewal
docker exec cohesity-cert-manager /scripts/cert_renewal.sh
```

### Updating the Container

To update the container with the latest code:

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Certificate validation fails**
   - Ensure port 80 is accessible from the internet to your Docker host
   - Check firewall rules

2. **Deployment to Cohesity fails**
   - Verify SSH key permissions (ssh method)
   - Check Cohesity credentials (api method)
   - Ensure network connectivity to the Cohesity cluster

3. **Container exits unexpectedly**
   - Check logs for errors: `docker-compose logs`
   - Ensure all environment variables are set correctly

## Security Considerations

1. Store sensitive information like passwords in environment variables or use a secrets management solution.
2. Keep the SSH private key secure with proper file permissions (600).
3. Consider using a non-root user in the Docker container.
4. Implement network-level security to restrict access to the certificate management server.
