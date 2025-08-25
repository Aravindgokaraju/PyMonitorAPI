#!/usr/bin/env python
"""
Script to run Django in production mode locally on Windows
"""
import os
import sys
import subprocess
from pathlib import Path

def load_env_file(env_file):
    """Load environment variables from a file"""
    env_vars = {}
    if Path(env_file).exists():
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle lines with = sign
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                        os.environ[key.strip()] = value.strip()
    return env_vars

def run_command(cmd, check=True):
    """Run a command and print output"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result

def main():
    # Set environment to production
    os.environ['DJANGO_ENV'] = 'production_local'
    
    # Load environment variables from .env.production
    env_vars = load_env_file('.env.production_local')
    
    # Ensure required environment variables are set
    required_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    for var in required_vars:
        if var not in os.environ:
            print(f"Error: Required environment variable {var} is not set")
            sys.exit(1)
    
    # Run Django management commands
    print("=" * 50)
    print("Setting up Django production server")
    print("=" * 50)
    
    # Collect static files
    print("\n1. Collecting static files...")
    run_command(['python', 'manage.py', 'collectstatic', '--noinput'])
    
    # Make migrations
    print("\n2. Checking for migrations...")
    run_command(['python', 'manage.py', 'makemigrations'], check=False)
    
    # Apply migrations
    print("\n3. Applying migrations...")
    run_command(['python', 'manage.py', 'migrate'])
    
    # Check deployment settings
    print("\n4. Checking deployment configuration...")
    run_command(['python', 'manage.py', 'check', '--deploy'])
    
    # Start Waitress
    print("\n5. Starting Waitress production server...")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start Waitress - this will block until stopped
    run_command(['python', 'waitress_server.py'], check=False)

if __name__ == '__main__':
    main()