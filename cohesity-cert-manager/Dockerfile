FROM ubuntu:22.04

# Set environment variables to make installation non-interactive
ENV DEBIAN_FRONTEND=noninteractive

ENV TZ=America/Los_Angeles

# Install required packages
RUN apt-get update && \
    apt-get install -y certbot openssh-client python3 python3-pip cron curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install requests

# Create directories
RUN mkdir -p /etc/letsencrypt /scripts /ssh

# Copy scripts - adjust paths to match your actual directory structure
COPY scripts/cert_renewal.sh /scripts/
COPY scripts/deploy_cert.py /scripts/
COPY scripts/entrypoint.sh /scripts/

# Make scripts executable
RUN chmod +x /scripts/*.sh /scripts/*.py

# Add SSH key placeholder - will be volume mounted later
RUN touch /ssh/ssh_key && chmod 600 /ssh/ssh_key

# Set up cron job
RUN echo "0 3 1 * * /scripts/cert_renewal.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/cert-renew && \
    chmod 0644 /etc/cron.d/cert-renew
    ## have cron run by kubernetes

# Create log file
RUN touch /var/log/cron.log

# Set entrypoint
ENTRYPOINT ["/scripts/entrypoint.sh"]

# Keep container running
CMD ["cron", "-f"]
