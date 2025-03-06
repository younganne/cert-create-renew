#!/bin/bash
set -e

# Log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> /var/log/cron.log
}

log "Starting certificate renewal process for $DOMAIN"

# Run certbot renewal
certbot renew --quiet

# Check if certificates were renewed by comparing modification time
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
LAST_DEPLOY_RECORD="/etc/letsencrypt/last_deploy"

if [ ! -f "$LAST_DEPLOY_RECORD" ] || [ "$CERT_PATH" -nt "$LAST_DEPLOY_RECORD" ]; then
    log "Certificate was renewed or initial deployment needed, deploying to Cohesity cluster"
    
    # Deploy certificate to Cohesity cluster
    if [ "$DEPLOY_METHOD" = "api" ]; then
        log "Using API method for deployment"
        # Read password from Docker secret
        COHESITY_PASSWORD=$(cat /run/secrets/cohesity_password)
        python3 /scripts/deploy_cert.py \
            --cluster "$COHESITY_HOST" \
            --username "$COHESITY_USER" \
            --password "$COHESITY_PASSWORD" \
            --cert-dir "/etc/letsencrypt/live/$DOMAIN"
    else
        log "Using SSH method for deployment"
        # Create combined PEM file
        cat "/etc/letsencrypt/live/$DOMAIN/privkey.pem" \
            "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" > /tmp/cohesity_cert.pem
            
        # Deploy via SSH
        scp -i /ssh/ssh_key -o StrictHostKeyChecking=no /tmp/cohesity_cert.pem \
            "$COHESITY_USER@$COHESITY_HOST:/tmp/"
            
        ssh -i /ssh/ssh_key -o StrictHostKeyChecking=no "$COHESITY_USER@$COHESITY_HOST" \
            "cohesity_cluster_cli ssl_certificate update /tmp/cohesity_cert.pem && \
             rm /tmp/cohesity_cert.pem"
             
        # Clean up
        rm /tmp/cohesity_cert.pem
    fi
    
    # Update deployment record
    touch "$LAST_DEPLOY_RECORD"
    log "Certificate deployment completed successfully"
else
    log "No new certificate found, skipping deployment"
fi
