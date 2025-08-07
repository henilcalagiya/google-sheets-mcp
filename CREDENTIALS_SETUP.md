# Google Credentials Setup Guide

This guide shows you how to extract your Google credentials from your JSON file and fill out the MCP configuration template.

## 📋 Step-by-Step Instructions

### Step 1: Get Your Google Credentials JSON File

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON credentials file

### Step 2: Extract Credentials from JSON File

Open your downloaded JSON file. It will look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-123456",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-123456.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-123456.iam.gserviceaccount.com"
}
```

### Step 3: Fill Out the Template

Copy `mcp_config_template.json` to `mcp_config.json` and fill in the values:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "python", "-m", "gsheet_mcp_server"],
      "cwd": "/path/to/your/gsheet-mcp-server",
      "env": {
        "GOOGLE_PROJECT_ID": "your-project-123456",
        "GOOGLE_PRIVATE_KEY_ID": "abc123def456...",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "your-service-account@your-project-123456.iam.gserviceaccount.com",
        "GOOGLE_CLIENT_ID": "123456789012345678901",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-123456.iam.gserviceaccount.com"
      }
    }
  }
}
```

### Step 4: Mapping Guide

| Template Field | JSON Field | Example |
|----------------|------------|---------|
| `GOOGLE_PROJECT_ID` | `project_id` | `"your-project-123456"` |
| `GOOGLE_PRIVATE_KEY_ID` | `private_key_id` | `"abc123def456..."` |
| `GOOGLE_PRIVATE_KEY` | `private_key` | `"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"` |
| `GOOGLE_CLIENT_EMAIL` | `client_email` | `"your-service-account@your-project-123456.iam.gserviceaccount.com"` |
| `GOOGLE_CLIENT_ID` | `client_id` | `"123456789012345678901"` |
| `GOOGLE_CLIENT_X509_CERT_URL` | `client_x509_cert_url` | `"https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-123456.iam.gserviceaccount.com"` |

### Step 5: Update Path

Change the `cwd` path to your actual project directory:

```json
"cwd": "/Users/yourusername/path/to/gsheet-mcp-server"
```

## 🔧 Quick Setup Commands

```bash
# 1. Copy the template
cp mcp_config_template.json mcp_config.json

# 2. Edit the file with your credentials
nano mcp_config.json
# or
code mcp_config.json
# or
vim mcp_config.json

# 3. Test the configuration
python3 test_server.py
```

## ⚠️ Important Notes

### **Private Key Formatting:**
- The `private_key` must include the `\n` characters
- Keep the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines
- The key should be on multiple lines with `\n` separators

### **Path Updates:**
- Update `cwd` to your actual project directory
- Use absolute paths for reliability

### **Security:**
- Never commit `mcp_config.json` to version control
- Keep your credentials secure
- The template file is safe to share

## 🧪 Testing

After filling out the template:

```bash
# Test the server
python3 test_server.py

# Expected output:
# ✅ Server started successfully (timed out as expected)
# 🎉 MCP server is working correctly!
```

## 🆘 Troubleshooting

### **"Missing environment variables"**
- Check that all fields are filled in `mcp_config.json`
- Verify the private key includes `\n` characters
- Ensure no extra spaces or quotes

### **"Authentication failed"**
- Verify your Google Cloud APIs are enabled
- Check that your service account has correct permissions
- Share your Google Sheets with the service account email

### **"Cannot access Google Sheets"**
- Share your Google Sheets with the service account email
- Give "Editor" permissions to the service account

## 📝 Example Completed Config

Here's what a completed `mcp_config.json` looks like:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "python", "-m", "gsheet_mcp_server"],
      "cwd": "/Users/john/Documents/gsheet-mcp-server",
      "env": {
        "GOOGLE_PROJECT_ID": "my-awesome-project-123",
        "GOOGLE_PRIVATE_KEY_ID": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
        "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCq1LyRiC9OgKdO\nSfmJrrJ1Vs8nU/Vlq2Lpe5AtCzPZZLs0/hSTuIbIoB4MLwFn6xk4DsvzmUHtuvnI\n7JS5TSc2nZE/ln8+AEKZTzl+B/WjHWEVQxxC+Y9c+RgYRb7p42ZeiEV9RB33RNsr\ne4q11f1+Qqih+8U/d7Bt7ZLog6HmxBgbkQpnzowqUTQV5G9n2CMgvUWUzqqT986F\naNHDv3tu98cAg3bcXBvQSl0aDF7INlHqgjsKv0TRdXSgqMJUUQsLu5LWTZVRvXT1\n8K5A/UMQUDE/rND+SYaarb4awL0s3vaRDObZW6HSHwiewkHY+QBcAcdL18csOLXh\n2LfRXmc7AgMBAAECggEACNm3uaxuTAEhTRwQoZXJ+A4rhInvh8Nr2OzlRC1V6O2Y\n+KhS0jZ0Lf+K4l6rKOV9b9Vu7mFqULFpVJ9GA63aun45yTG83fNYjzqjKhLWuS0U\nSZ7b49JQCusAc3m9dkcxxoJQTCZTEsyvjfX8BlpoUWflvyUkC/5Q0fPQQ58ibPYI\ni1UMMc+KWbdof+fofgFZ0Ca1ccnEHJWgu8O2rQkBx9E3Nxd7BoiAXpdnFBxLK/+x\nSmZkKG+3Gpbi2GoMGnd8DUSJgDcsu6NMDJ+HKK48FdxNQ6k8LEPaBneitq1R/3qf\nQJKU5Ido9hVJ1gK2G3Cy566MeVLf1TivyWAZP6kqcQKBgQD/VV7Y0/XzQpnq+QBo\nU+dzFN0klFNT2wzAqFOYo6/j5YxBj0i74Nihd0QTBj2xVNoCIODzcrYQaoQoXOoN\n15n/T1swfHDcc9/Ti7t/3ZLnbGpQ6fogVSbgm177S1FWA8F87okAh+2vYJJFpkmo\nTCfQbbqs/LmFumCrXhBfbFz4nQKBgQDrcapDG6WWfqVvvUn4yLYLTfI0b3ZfzoDJ\nUH7k45Da0d4LUXE8HwI+iSONFOipsGu5fp/6Za2hnGx8OHV6mccpF7qujgdTNirG\nHO7u78/ZdC6EgqCsXAWZHMcSlWQjtZd93THeiIlcoJQGaWLSidTh84Q8hlL+ex41\nAJTfkia7twKBgQDIGX9bLcFyAp/dJYbMO/UGmzMzl4o2DVTRJxlcZetSDnL8be3y\nTyN2ZqFSx3FRp82yHVItd5h3BQLNHwPOFUj6bJZqSRupqKWgg8FNU7fs5WnsP3Fm\nJVVycFDfXwc/AXKBFe8IG36KEoSPUOIoooYRMe055FUAGC/qHK14GtRBgQKBgQDP\n5JG+p87S0AksXSvP7QoxeSYAfts7RZAaMmWZngbt8JnrzIH74DWPGnC1xlyaWRkF\ntXV1GAr0xLZWCVRSaS6ebkF8mBSHuTCTtkCT4lTZYekhQGa3Spn21J5DHn5JubKG\nhKXgJReFHpUWBEAqP2ImEWwWNVVbN0M48caCkv54iQKBgAUNESHRCMI+xQIpQc74\niVpuZ3KedSeKeSuAM3MuKmQizVRmX9GDmeVXCxg8J3V4q2JG62wJ3VxG0ZuNnR19\nYE7CxBQjFJ9sypbAdzcxWT7/mKlQpeHQ7h91dulmlS2APo7FfFvB9Y/flOvdUXbZ\nQaPx7ndUTgsovSBCxC5k+vut\n-----END PRIVATE KEY-----\n",
        "GOOGLE_CLIENT_EMAIL": "my-service-account@my-awesome-project-123.iam.gserviceaccount.com",
        "GOOGLE_CLIENT_ID": "123456789012345678901",
        "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
        "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
        "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
        "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/my-service-account%40my-awesome-project-123.iam.gserviceaccount.com"
      }
    }
  }
}
```

**That's it! You're ready to use all 23 Google Sheets tools!** 🎉 