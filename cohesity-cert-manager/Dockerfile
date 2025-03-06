FROM ubuntu:22.04

# Install required packages
RUN apt-get update && \
    apt-get install -y certbot openssh-client python3 python3-pip cron curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install requests

# Create directories
RUN mkdir -p /etc/letsencrypt /scripts /ssh

# Copy scripts
COPY cert_renewal.sh /scripts/
COPY deploy_cert.py /scripts/
COPY entrypoint.sh /scripts/

# Make scripts executable
RUN chmod +x /scripts/*.sh /scripts/*.py

# Add SSH key (you'll need to provide this during build)
COPY ssh_key /ssh/
RUN chmod 600 /ssh/ssh_key

# Set up cron job
RUN echo "0 3 1 * * /scripts/cert_renewal.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/cert-renew && \
    chmod 0644 /etc/cron.d/cert-renew

# Create log file
RUN touch /var/log/cron.log

# Set entrypoint
ENTRYPOINT ["/scripts/entrypoint.sh"]

# Keep container running
CMD ["cron", "-f"]
