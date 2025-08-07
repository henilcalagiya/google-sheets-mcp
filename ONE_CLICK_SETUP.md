# 🚀 One-Click Setup for Non-Technical Users

This guide is for people who want to use the Google Sheets MCP server with minimal technical knowledge.

## 📋 What You Need

1. **Google Account** (Gmail)
2. **Computer** (Windows, Mac, or Linux)
3. **Basic text editing** (like Notepad)

## 🎯 Super Simple Setup (3 Steps)

### Step 1: Get Your Google Credentials (5 minutes)

1. **Go to Google Cloud Console:**
   - Open: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a Project:**
   - Click "Select a project" → "New Project"
   - Name it: "My Google Sheets MCP"
   - Click "Create"

3. **Enable APIs:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API" → Click → "Enable"
   - Search for "Google Drive API" → Click → "Enable"

4. **Create Service Account:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: "google-sheets-mcp"
   - Click "Create and Continue"
   - Click "Done"

5. **Download Credentials:**
   - Click on your service account (google-sheets-mcp@...)
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" → Click "Create"
   - **Save the file** (remember where!)

### Step 2: Download and Setup (2 minutes)

1. **Download the server:**
   - Go to: https://github.com/henilcalagiya/google-sheets-mcp
   - Click the green "Code" button
   - Click "Download ZIP"
   - Extract the ZIP file to your Desktop

2. **Run setup:**
   - Open Terminal/Command Prompt
   - Navigate to the extracted folder:
     ```bash
     # On Mac/Linux:
     cd ~/Desktop/gsheet-mcp-server
     
     # On Windows:
     cd C:\Users\YourName\Desktop\gsheet-mcp-server
     ```
   - Run the setup:
     ```bash
     # On Mac/Linux:
     chmod +x setup.sh
     ./setup.sh
     
     # On Windows:
     setup.bat
     ```

### Step 3: Configure (3 minutes)

1. **Run the helper script:**
   ```bash
   python3 setup_config.py
   ```

2. **Edit the configuration:**
   - Open `mcp_config.json` in any text editor (Notepad, TextEdit, etc.)
   - Replace the placeholder values with your real credentials:

   **Find these lines and replace them:**

   ```json
   "GOOGLE_PROJECT_ID": "your-project-id-here",
   ```
   → Replace with your project ID (from Step 1, project name)

   ```json
   "GOOGLE_PRIVATE_KEY_ID": "your-private-key-id-here",
   ```
   → Replace with the `private_key_id` from your downloaded JSON file

   ```json
   "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n",
   ```
   → Replace with the entire `private_key` from your JSON file

   ```json
   "GOOGLE_CLIENT_EMAIL": "your-service-account@your-project.iam.gserviceaccount.com",
   ```
   → Replace with the `client_email` from your JSON file

   ```json
   "GOOGLE_CLIENT_ID": "your-client-id-here",
   ```
   → Replace with the `client_id` from your JSON file

   ```json
   "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
   ```
   → Replace with the `client_x509_cert_url` from your JSON file

3. **Update the path:**
   ```json
   "cwd": "/path/to/your/gsheet-mcp-server",
   ```
   → Replace with your actual folder path (e.g., `/Users/YourName/Desktop/gsheet-mcp-server`)

4. **Test it:**
   ```bash
   python3 test_server.py
   ```

## 🎉 You're Done!

Now you can use all 23 Google Sheets tools in your MCP client!

## 📱 How to Use

1. **Open your MCP client** (Claude Desktop, Continue, etc.)
2. **Add the server configuration** (copy the JSON from `mcp_config.json`)
3. **Share your Google Sheets** with the service account email
4. **Start using the tools!**

## 🆘 Need Help?

### **"I can't find the JSON file"**
- Check your Downloads folder
- Look for a file ending in `.json`
- It was downloaded when you created the service account key

### **"I don't know what to copy"**
- Open your JSON file in a text editor
- Look for lines like `"project_id": "something"`
- Copy the value between the quotes (not the quotes themselves)

### **"The test failed"**
- Make sure you copied all the values correctly
- Check that you didn't add extra spaces
- Verify the `cwd` path is correct

### **"I can't access my Google Sheets"**
- Share your Google Sheets with the service account email
- Give it "Editor" permissions
- The email is in your JSON file under `client_email`

## 💡 Pro Tips

- **Save your JSON file** - You'll need it again if you reinstall
- **Keep it secure** - Don't share your JSON file with others
- **Test first** - Always run `python3 test_server.py` before using
- **Start small** - Try with one Google Sheet first

**That's it! You now have a powerful Google Sheets AI assistant!** 🚀 