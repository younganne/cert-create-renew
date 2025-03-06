#!/usr/bin/env python3

import requests
import json
import base64
import argparse
import os
import sys
import urllib3
from datetime import datetime

# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def log(message):
    """Write log message to standard output and log file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open('/var/log/cron.log', 'a') as log_file:
        log_file.write(log_message + '\n')

def upload_cert_to_cohesity(cluster, username, password, cert_dir):
    """
    Uploads and installs a SSL certificate to a Cohesity cluster using the REST API.
    
    Args:
        cluster (str): Hostname or IP of the Cohesity cluster
        username (str): Admin username for the Cohesity cluster
        password (str): Password for the admin user
        cert_dir (str): Directory containing the certificate files
    """
    try:
        # Combine certificate files
        with open(os.path.join(cert_dir, 'privkey.pem'), 'r') as key_file:
            private_key = key_file.read()
            
        with open(os.path.join(cert_dir, 'fullchain.pem'), 'r') as cert_file:
            certificate = cert_file.read()
            
        combined_cert = private_key + certificate
        
        # Authentication
        log(f"Authenticating to Cohesity cluster {cluster}")
        auth_url = f"https://{cluster}/irisservices/api/v1/public/accessTokens"
        auth_body = {
            "username": username,
            "password": password
        }
        
        # Get authentication token
        auth_response = requests.post(auth_url, json=auth_body, verify=False, timeout=30)
        if auth_response.status_code != 201:
            raise Exception(f"Authentication failed: {auth_response.text}")
        
        token = auth_response.json().get('accessToken')
        log("Authentication successful")
        
        # Base64 encode the certificate
        cert_encoded = base64.b64encode(combined_cert.encode()).decode()
        
        # Prepare certificate installation request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        cert_url = f"https://{cluster}/irisservices/api/v1/public/certificates"
        cert_body = {
            "certificate": cert_encoded,
            "useForClusterAccess": True
        }
        
        # Upload and install certificate
        log("Uploading certificate to Cohesity cluster")
        cert_response = requests.post(cert_url, headers=headers, json=cert_body, verify=False, timeout=60)
        
        if cert_response.status_code == 200:
            log("Certificate successfully uploaded and installed")
            return True
        else:
            log(f"Certificate installation failed: {cert_response.text}")
            return False
            
    except Exception as e:
        log(f"Error during certificate deployment: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload SSL certificate to Cohesity cluster')
    parser.add_argument('--cluster', required=True, help='Cohesity cluster hostname or IP')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--password', required=True, help='Admin password')
    parser.add_argument('--cert-dir', required=True, help='Directory containing certificate files')
    
    args = parser.parse_args()
    
    success = upload_cert_to_cohesity(args.cluster, args.username, args.password, args.cert_dir)
    if not success:
        sys.exit(1)
