# Cohesity Certificate Manager Environment Variables

# Domain for the certificate
DOMAIN=example.com

# Contact email for Let's Encrypt
EMAIL=user@example.com

# Cohesity cluster details
COHESITY_HOST=cluster.example.com
COHESITY_USER=adminuser
# COHESITY_PASSWORD is now stored in Docker Secrets

# Deployment method (options: ssh, api)
DEPLOY_METHOD=ssh
