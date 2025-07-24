# Google Sheets MCP Server Setup Guide

This guide will walk you through setting up the Google Sheets MCP Server step by step.

## Prerequisites

- Python 3.8 or higher
- A Google account
- Access to Google Cloud Console

## Step 1: Install Dependencies

First, install the required Python packages:

```bash
# Install the package in development mode
pip install -e .

# Or install dependencies manually
pip install mcp google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pydantic
```

## Step 2: Set Up Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a New Project**
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "MCP Google Sheets")
   - Click "Create"

3. **Enable Google Sheets API**
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click on it and then click "Enable"

4. **Enable Google Drive API**
   - Go back to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and then click "Enable"

## Step 3: Create Service Account Credentials

1. **Go to Credentials**
   - In the left sidebar, go to "APIs & Services" > "Credentials"

2. **Create Service Account**
   - Click "Create Credentials" > "Service Account"
   - Enter a service account name (e.g., "mcp-sheets-server")
   - Click "Create and Continue"

3. **Grant Access**
   - For "Role", select "Editor" (or create a custom role with minimal permissions)
   - Click "Continue"
   - Click "Done"

4. **Create Key**
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON" format
   - Click "Create"
   - The JSON file will download automatically

## Step 4: Configure the Server

1. **Save the Credentials**
   - Move the downloaded JSON file to a secure location
   - Note the path to the file

2. **Set Environment Variable**
   ```bash
   export GOOGLE_CREDENTIALS_PATH="/path/to/your/credentials.json"
   ```

3. **Share Google Sheets**
   - Open the JSON file and find the `client_email` field
   - Share any Google Sheets you want to access with this email address
   - Give it "Editor" permissions

## Step 5: Test the Server

1. **Run the Server**
   ```bash
   python -m gsheet_mcp_server
   ```

2. **Test with the Example Client**
   ```bash
   python examples/test_client.py
   ```

## Step 6: Integrate with MCP Client

Add this configuration to your MCP client (e.g., Claude Desktop, Continue):

```json
{
  "mcpServers": {
    "gsheet": {
      "command": "python",
      "args": ["-m", "gsheet_mcp_server"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/path/to/your/credentials.json"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Make sure the `GOOGLE_CREDENTIALS_PATH` environment variable is set correctly
   - Verify the file path exists and is readable

2. **"Permission denied" errors**
   - Make sure you've shared your Google Sheets with the service account email
   - Check that the service account has the necessary permissions

3. **"API not enabled" errors**
   - Go back to Google Cloud Console and ensure both Google Sheets API and Google Drive API are enabled

4. **Import errors**
   - Make sure you've installed all dependencies: `pip install -e .`

### Getting Help

- Check the [Google Sheets API documentation](https://developers.google.com/sheets/api)
- Review the [MCP Python SDK documentation](https://github.com/modelcontextprotocol/python-sdk)
- Check the server logs for detailed error messages

## Security Best Practices

1. **Keep credentials secure**
   - Don't commit the JSON file to version control
   - Use environment variables or secure secret management
   - Rotate credentials regularly

2. **Minimize permissions**
   - Only grant the minimum necessary permissions to the service account
   - Consider using custom roles with specific permissions

3. **Monitor usage**
   - Set up billing alerts in Google Cloud Console
   - Monitor API usage in the Google Cloud Console

## Next Steps

Once your server is running, you can:

1. **Extend the functionality**
   - Add more tools to the server
   - Implement additional Google Sheets features
   - Add support for other Google APIs

2. **Improve error handling**
   - Add better error messages
   - Implement retry logic
   - Add logging

3. **Add tests**
   - Write unit tests for your tools
   - Add integration tests
   - Set up CI/CD

4. **Deploy**
   - Package the server for distribution
   - Deploy to a cloud platform
   - Share with others 