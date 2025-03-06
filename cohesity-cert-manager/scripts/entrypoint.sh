#!/bin/bash
set -e

# Check for required secrets
if [ -f "/run/secrets/cohesity_password" ]; then
    echo "Cohesity password secret found"
else
    echo "ERROR: Cohesity password secret not found"
    exit 1
fi

# Initialize certificates if needed
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "Initial certificate request for $DOMAIN"
    certbot certonly --standalone -d $DOMAIN --agree-tos --email $EMAIL --non-interactive --staging
    
    # Deploy certificates immediately after initial request
    /scripts/cert_renewal.sh
fi

# Start cron service
echo "Starting cron service for scheduled renewals"
cron

# Tail the log to keep container running and provide visibility
tail -f /var/log/cron.log