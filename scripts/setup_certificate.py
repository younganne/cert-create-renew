#!/usr/bin/env python3
import subprocess
import sys
import os
import argparse
from typing import List, Tuple

def run_command(command: List[str]) -> Tuple[int, str, str]:
    """
    Execute a shell command and return its exit code, stdout, and stderr
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def check_root() -> bool:
    """Check if the script is running with root privileges"""
    return os.geteuid() == 0

def update_system() -> bool:
    """Update package lists and upgrade system packages"""
    print("Updating system packages...")
    
    commands = [
        ["apt-get", "update"],
        ["apt-get", "upgrade", "-y"]
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd)
        if code != 0:
            print(f"Error updating system: {stderr}")
            return False
    return True

def install_certbot() -> bool:
    """Install Certbot and its dependencies"""
    print("Installing Certbot...")
    
    commands = [
        ["apt-get", "install", "-y", "software-properties-common"],
        ["apt-get", "install", "-y", "certbot"]
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd)
        if code != 0:
            print(f"Error installing Certbot: {stderr}")
            return False
    return True

def obtain_certificate(domain: str, email: str, webroot_path: str = None) -> bool:
    """
    Obtain Let's Encrypt certificate using Certbot
    """
    print(f"Obtaining certificate for {domain}...")
    
    cmd = ["certbot", "certonly", "--non-interactive", "--agree-tos", "-m", email]
    
    if webroot_path:
        cmd.extend(["--webroot", "-w", webroot_path])
    else:
        cmd.append("--standalone")
    
    cmd.extend(["-d", domain])
    
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"Error obtaining certificate: {stderr}")
        return False
        
    print(stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="Automate Let's Encrypt certificate installation")
    parser.add_argument("domain", help="Domain name to obtain certificate for")
    parser.add_argument("email", help="Email address for important notifications")
    parser.add_argument("--webroot", help="Path to webroot for webroot authentication")
    args = parser.parse_args()

    if not check_root():
        print("This script must be run as root!")
        sys.exit(1)

    steps = [
        ("Updating system", update_system),
        ("Installing Certbot", install_certbot),
        ("Obtaining certificate", lambda: obtain_certificate(args.domain, args.email, args.webroot))
    ]

    for step_name, step_func in steps:
        print(f"\n=== {step_name} ===")
        if not step_func():
            print(f"\nError during {step_name.lower()}. Exiting.")
            sys.exit(1)

    print("\nSuccess! Your certificate has been obtained.")
    print(f"Certificate files are located in /etc/letsencrypt/live/{args.domain}/")
    print("\nTo use these certificates, configure your web server with:")
    print(f"  - Certificate: /etc/letsencrypt/live/{args.domain}/fullchain.pem")
    print(f"  - Private key: /etc/letsencrypt/live/{args.domain}/privkey.pem")

if __name__ == "__main__":
    main()