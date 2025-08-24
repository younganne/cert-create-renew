#!/bin/bash

# Certificate paths
#CERT_DIR="" # path to Let's Encrypt cert
#COHESITY_HOST=""  # Cohesity cluster hostname
#COHESITY_USER=""  # Cohesity SSH user
#SSH_KEY=""        # path to SSH key

# Create PEM file with full chain and private key
#cat $CERT_DIR/privkey.pem $CERT_DIR/fullchain.pem > /tmp/cohesity_cert.pem
sudo cat $CERT_DIR/fullchain.pem > /tmp/cohesity_cert.pem
sudo cat $CERT_DIR/privkey.pem > /tmp/privkey.pem

# Upload certificate to Cohesity
scp -i $SSH_KEY /tmp/privkey.pem /tmp/cohesity_cert.pem $COHESITY_USER@$COHESITY_HOST:/home/$COHESITY_USER/certs/
chmod 600 /home/support/certs/cohesity_cert.pem
chmod 400 /home/support/certs/privkey.pem

# Install certificate via SSH and Cohesity CLI command
iris_cli
ssh -i $SSH_KEY $COHESITY_USER@$COHESITY_HOST "cohesity_cluster_cli ssl_certificate update /tmp/cohesity_cert.pem"
iris_cli cluster update-ssl-certificate ssl-certificate=/tmp/cohesity_cert.pem ssl-cert-private-key=/tmp/privkey.pem

# Clean up
#rm /tmp/cohesity_cert.pem
