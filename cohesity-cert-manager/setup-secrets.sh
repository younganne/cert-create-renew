#!/bin/bash
# This script helps set up Docker Secrets for the Cohesity certificate manager

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Check if password exists
if [ -f "secrets/cohesity_password.txt" ]; then
    echo "Password secret already exists"
else
    # Prompt for password
    read -s -p "Enter Cohesity admin password: " PASSWORD
    echo
    
    # Write password to file
    echo "$PASSWORD" > secrets/cohesity_password.txt
    
    # Set proper permissions
    chmod 600 secrets/cohesity_password.txt
    echo "Password secret created successfully"
fi

echo "Docker secrets are ready to use"
