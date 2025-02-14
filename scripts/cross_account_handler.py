import boto3
import botocore
from typing import Optional, Dict, Any, Tuple
import json
import time

class CrossAccountManager:
    def __init__(self, dns_account_id: str, dns_role_name: str, external_id: str):
        self.dns_account_id = dns_account_id
        self.dns_role_name = dns_role_name
        self.external_id = external_id
        self.dns_session = None
        self.credentials = None
        self._max_retries = 3
        self._retry_delay = 5  # seconds

    def assume_dns_role(self) -> Tuple[bool, Optional[str]]:
        """
        Assume the Route53 DNS role in the other account
        Returns: (success, error_message)
        """
        try:
            sts = boto3.client('sts')
            role_arn = f"arn:aws:iam::{self.dns_account_id}:role/{self.dns_role_name}"

            for attempt in range(self._max_retries):
                try:
                    response = sts.assume_role(
                        RoleArn=role_arn,
                        RoleSessionName=f"CertbotDNS-{int(time.time())}",
                        ExternalId=self.external_id,
                        DurationSeconds=900
                    )

                    self.credentials = response['Credentials']
                    self.dns_session = boto3.Session(
                        aws_access_key_id=self.credentials['AccessKeyId'],
                        aws_secret_access_key=self.credentials['SecretAccessKey'],
                        aws_session_token=self.credentials['SessionToken']
                    )
                    return True, None

                except botocore.exceptions.ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    
                    if error_code == 'AccessDenied':
                        return False, self._handle_access_denied(e)
                    elif error_code == 'ExpiredToken':
                        if attempt < self._max_retries - 1:
                            time.sleep(self._retry_delay)
                            continue
                        return False, "Token expired and max retries reached"
                    else:
                        return False, f"AWS Error: {str(e)}"

        except Exception as e:
            return False, f"Unexpected error during role assumption: {str(e)}"

    def _handle_access_denied(self, error: botocore.exceptions.ClientError) -> str:
        """Handle access denied errors with detailed messaging"""
        error_message = error.response.get('Error', {}).get('Message', '')
        
        if "not authorized to perform: sts:AssumeRole" in error_message:
            return """Access Denied: Role assumption failed. Please check:
            1. Trust relationship in DNS account role
            2. External ID matches configuration
            3. App account role has permission to assume DNS role"""
        elif "role/certbot-dns-role not found" in error_message:
            return "Role not found: The specified DNS role does not exist"
        else:
            return f"Access Denied: {error_message}"

    def verify_route53_access(self, hosted_zone_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify access to Route53 hosted zone
        Returns: (success, error_message)
        """
        if not self.dns_session:
            return False, "No DNS session established. Call assume_dns_role first."

        try:
            route53 = self.dns_session.client('route53')
            
            # Test listing zones first (less restrictive)
            try:
                route53.list_hosted_zones(MaxItems='1')
            except botocore.exceptions.ClientError as e:
                return False, self._handle_route53_error(e, "list zones")

            # Test specific zone access
            try:
                route53.get_hosted_zone(Id=hosted_zone_id)
                return True, None
            except botocore.exceptions.ClientError as e:
                return False, self._handle_route53_error(e, "access zone")

        except Exception as e:
            return False, f"Unexpected error accessing Route53: {str(e)}"

    def _handle_route53_error(self, error: botocore.exceptions.ClientError, action: str) -> str:
        """Handle Route53-specific errors"""
        error_code = error.response.get('Error', {}).get('Code', '')
        error_message = error.response.get('Error', {}).get('Message', '')

        if error_code == 'AccessDenied':
            return f"""Route53 Access Denied: Unable to {action}. Please check:
            1. DNS role has correct Route53 permissions
            2. Hosted zone exists in DNS account
            3. IAM policy includes required Route53 actions"""
        elif error_code == 'NoSuchHostedZone':
            return f"Hosted zone not found: {error_message}"
        else:
            return f"Route53 Error: {error_message}"

def setup_cross_account_access(dns_account_id: str, dns_role_name: str, 
                             external_id: str, hosted_zone_id: str) -> Tuple[bool, Optional[str], Optional[Any]]:
    """
    Set up and verify cross-account access
    Returns: (success, error_message, dns_session)
    """
    manager = CrossAccountManager(dns_account_id, dns_role_name, external_id)
    
    # Step 1: Assume role
    success, error = manager.assume_dns_role()
    if not success:
        return False, f"Failed to assume DNS role: {error}", None

    # Step 2: Verify Route53 access
    success, error = manager.verify_route53_access(hosted_zone_id)
    if not success:
        return False, f"Failed to verify Route53 access: {error}", None

    return True, None, manager.dns_session