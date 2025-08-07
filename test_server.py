#!/usr/bin/env python3
"""
Test script to verify the MCP server starts correctly.
"""

import os
import sys
import subprocess

def test_server_startup():
    """Test if the server starts correctly with environment variables."""
    
    # Set environment variables from mcp_config.json
    env_vars = {
        "GOOGLE_PROJECT_ID": "glossy-chimera-466301-c1",
        "GOOGLE_PRIVATE_KEY_ID": "a4ae73111b11b2c3b07cc01006e71eb8230dfa29",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDq1LyRiC9OgKdO\nSfmJrrJ1Vs8nU/Vlq2Lpe5AtCzPZZLs0/hSTuIbIoB4MLwFn6xk4DsvzmUHtuvnI\n7JS5TSc2nZE/ln8+AEKZTzl+B/WjHWEVQxxC+Y9c+RgYRb7p42ZeiEV9RB33RNsr\ne4q11f1+Qqih+8U/d7Bt7ZLog6HmxBgbkQpnzowqUTQV5G9n2CMgvUWUzqqT986F\naNHDv3tu98cAg3bcXBvQSl0aDF7INlHqgjsKv0TRdXSgqMJUUQsLu5LWTZVRvXT1\n8K5A/UMQUDE/rND+SYaarb4awL0s3vaRDObZW6HSHwiewkHY+QBcAcdL18csOLXh\n2LfRXmc7AgMBAAECggEACNm3uaxuTAEhTRwQoZXJ+A4rhInvh8Nr2OzlRC1V6O2Y\n+KhS0jZ0Lf+K4l6rKOV9b9Vu7mFqULFpVJ9GA63aun45yTG83fNYjzqjKhLWuS0U\nSZ7b49JQCusAc3m9dkcxxoJQTCZTEsyvjfX8BlpoUWflvyUkC/5Q0fPQQ58ibPYI\ni1UMMc+KWbdof+fofgFZ0Ca1ccnEHJWgu8O2rQkBx9E3Nxd7BoiAXpdnFBxLK/+x\nSmZkKG+3Gpbi2GoMGnd8DUSJgDcsu6NMDJ+HKK48FdxNQ6k8LEPaBneitq1R/3qf\nQJKU5Ido9hVJ1gK2G3Cy566MeVLf1TivyWAZP6kqcQKBgQD/VV7Y0/XzQpnq+QBo\nU+dzFN0klFNT2wzAqFOYo6/j5YxBj0i74Nihd0QTBj2xVNoCIODzcrYQaoQoXOoN\n15n/T1swfHDcc9/Ti7t/3ZLnbGpQ6fogVSbgm177S1FWA8F87okAh+2vYJJFpkmo\nTCfQbbqs/LmFumCrXhBfbFz4nQKBgQDrcapDG6WWfqVvvUn4yLYLTfI0b3ZfzoDJ\nUH7k45Da0d4LUXE8HwI+iSONFOipsGu5fp/6Za2hnGx8OHV6mccpF7qujgdTNirG\nHO7u78/ZdC6EgqCsXAWZHMcSlWQjtZd93THeiIlcoJQGaWLSidTh84Q8hlL+ex41\nAJTfkia7twKBgQDIGX9bLcFyAp/dJYbMO/UGmzMzl4o2DVTRJxlcZetSDnL8be3y\nTyN2ZqFSx3FRp82yHVItd5h3BQLNHwPOFUj6bJZqSRupqKWgg8FNU7fs5WnsP3Fm\nJVVycFDfXwc/AXKBFe8IG36KEoSPUOIoooYRMe055FUAGC/qHK14GtRBgQKBgQDP\n5JG+p87S0AksXSvP7QoxeSYAfts7RZAaMmWZngbt8JnrzIH74DWPGnC1xlyaWRkF\ntXV1GAr0xLZWCVRSaS6ebkF8mBSHuTCTtkCT4lTZYekhQGa3Spn21J5DHn5JubKG\nhKXgJReFHpUWBEAqP2ImEWwWNVVbN0M48caCkv54iQKBgAUNESHRCMI+xQIpQc74\niVpuZ3KedSeKeSuAM3MuKmQizVRmX9GDmeVXCxg8J3V4q2JG62wJ3VxG0ZuNnR19\nYE7CxBQjFJ9sypbAdzcxWT7/mKlQpeHQ7h91dulmlS2APo7FfFvB9Y/flOvdUXbZ\nQaPx7ndUTgsovSBCxC5k+vut\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "google-sheets-mcp@glossy-chimera-466301-c1.iam.gserviceaccount.com",
        "GOOGLE_CLIENT_ID": "113227823918217958816",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-mcp%40glossy-chimera-466301-c1.iam.gserviceaccount.com"
    }
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("🔧 Testing MCP server startup...")
    print("📋 Environment variables set:")
    for key in ["GOOGLE_PROJECT_ID", "GOOGLE_CLIENT_EMAIL", "GOOGLE_CLIENT_ID"]:
        print(f"  ✅ {key}: {os.environ.get(key, 'NOT SET')}")
    
    try:
        # Test server startup
        result = subprocess.run(
            ["uv", "run", "python", "-m", "gsheet_mcp_server"],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        if result.returncode == 0:
            print("✅ Server started successfully!")
            print("📝 Output:", result.stdout)
            return True
        else:
            print("❌ Server failed to start")
            print("📝 Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Server started successfully (timed out as expected)")
        return True
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    success = test_server_startup()
    if success:
        print("\n🎉 MCP server is working correctly!")
        print("💡 Your MCP client should be able to connect to it.")
    else:
        print("\n🚨 MCP server has issues. Check the error messages above.")
        sys.exit(1) 