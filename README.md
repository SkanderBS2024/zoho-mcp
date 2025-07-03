# Zoho CRM MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with Zoho CRM. This server exposes Zoho CRM functionality as MCP tools that can be used by AI assistants like Claude, GPT, and other MCP-compatible clients.

## Features

- **Full OAuth2 Authentication**: Secure authentication with Zoho CRM using OAuth2 flow
- **Environment Variables**: Secure credential management using .env files
- **Contact Management**: Search, create, and update contacts
- **Deal Management**: Search, create, and list deals
- **User Information**: Get current user details
- **STDIO Transport**: Compatible with MCP clients using standard input/output
- **Error Handling**: Comprehensive error handling with clear error messages
- **Token Management**: Automatic access token refresh
- **PyPI Ready**: Installable via pip/uvx for easy distribution

## Prerequisites

- Python 3.11 or higher
- Zoho CRM account with API access
- Zoho Developer Console app credentials

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install using uvx (recommended for CLI tools)
uvx zoho-crm-mcp

# Or install using pip
pip install zoho-crm-mcp
```

### Option 2: Install from Source

1. **Clone this repository**:
   ```bash
   git clone <repository-url>
   cd zoho-crm-mcp
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   # or
   pip install -e .
   ```

## Setup

### Step 1: Create Zoho Developer App

1. Go to [Zoho Developer Console](https://api-console.zoho.com/)
2. Create a new "Server-based Applications" app
3. Note down your `Client ID` and `Client Secret`
4. Set redirect URI to `http://localhost:8080/callback`

### Step 2: Configure Environment Variables

Create a `.env` file in your working directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your credentials:
```env
ZOHO_CLIENT_ID=your_actual_client_id
ZOHO_CLIENT_SECRET=your_actual_client_secret
ZOHO_REDIRECT_URI=http://localhost:8080/callback
ZOHO_API_DOMAIN=https://www.zohoapis.com
ZOHO_SCOPE=ZohoCRM.modules.ALL,ZohoCRM.users.READ
```

## Authentication Setup

Before running the MCP server, you need to generate authentication tokens manually:

### Step 1: Generate Tokens

Run the authentication helper to generate your tokens:

```bash
# Using uv (recommended)
uv run zoho-mcp-auth

# Or if installed via pip
zoho-mcp-auth
```

This will guide you through the OAuth flow:

```
🔐 Zoho CRM Manual Token Generation
===================================

Step 1: Visit the authorization URL
====================================
Please visit this URL to authorize the application:

https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL%2CZohoCRM.users.ALL%2CZohoCRM.org.ALL&client_id=your_client_id&response_type=code&redirect_uri=https%3A%2F%2Flocalhost&access_type=offline

Step 2: Get the authorization code
==================================
After authorization, you'll be redirected to your redirect_uri.
Copy the 'code' parameter from the redirect URL and paste it below.

Enter authorization code: [paste your code here]

✅ Token generation successful!

Step 3: Add tokens to your .env file
====================================
Add the following lines to your .env file:

ZOHO_ACCESS_TOKEN=your_generated_access_token
ZOHO_REFRESH_TOKEN=your_generated_refresh_token
```

### Step 2: Add Tokens to .env File

Copy the generated tokens and add them to your `.env` file:

```bash
# Authentication Tokens
ZOHO_ACCESS_TOKEN=your_generated_access_token_here
ZOHO_REFRESH_TOKEN=your_generated_refresh_token_here
```

⚠️ **Important**: Keep these tokens secure and never commit them to version control!

## Running the MCP Server

Once your tokens are configured, you can run the server:

```bash
# Using uv (recommended)
uv run zoho-mcp

# Or if installed via pip
zoho-mcp
```

The server will validate your authentication and start:

```
Fetching user information...
✓ Authenticated as: Your Name (your.email@example.com)
Zoho CRM MCP Server running on stdio
```

## Available MCP Tools

### 1. `get_contact_by_email_tool`
Search for a contact by email address.

**Parameters:**
- `email` (string): Email address to search for

**Returns:**
- Contact information including ID, name, phone, account, and timestamps

### 2. `create_contact_tool`
Create a new contact in Zoho CRM.

**Parameters:**
- `first_name` (string): Contact's first name
- `last_name` (string): Contact's last name
- `email` (string): Contact's email address
- `phone` (string): Contact's phone number

**Returns:**
- Created contact ID and status

### 3. `get_deal_by_name_tool`
Search for a deal by name.

**Parameters:**
- `deal_name` (string): Name of the deal to search for

**Returns:**
- Deal information including ID, amount, stage, contacts, and dates

### 4. `create_deal_tool`
Create a new deal in Zoho CRM.

**Parameters:**
- `deal_name` (string): Name of the deal
- `contact_id` (string): ID of the associated contact
- `stage` (string): Deal stage (e.g., 'Qualification', 'Proposal', 'Negotiation', 'Closed Won')
- `amount` (float): Deal amount

**Returns:**
- Created deal ID and status

### 5. `update_contact_tool`
Update a specific field of an existing contact.

**Parameters:**
- `contact_id` (string): ID of the contact to update
- `field` (string): Field name to update (e.g., 'Phone', 'Email', 'First_Name')
- `value` (string): New value for the field

**Returns:**
- Update status and confirmation

### 6. `list_open_deals_tool`
List all open deals (excluding closed deals).

**Parameters:** None

**Returns:**
- Array of open deals with details

### 7. `get_user_info_tool`
Get current authenticated user information.

**Parameters:** None

**Returns:**
- User information including name, email, role, and profile

## Usage with MCP Clients

### Claude Desktop

Add this server to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zoho-crm": {
      "command": "uvx",
      "args": ["zoho-crm-mcp"],
      "env": {}
    }
  }
}
```

**Alternative configuration if installed locally:**
```json
{
  "mcpServers": {
    "zoho-crm": {
      "command": "zoho-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### Other MCP Clients

For other MCP-compatible clients, configure them to run:
```bash
# If installed via PyPI
zoho-mcp

# Or using uvx
uvx zoho-crm-mcp
```

### Command Line Testing

You can test the server directly using JSON-RPC over STDIO:

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_user_info_tool", "arguments": {}}}' | zoho-mcp
```

## Error Handling

The server provides comprehensive error handling:

- **Authentication errors**: Clear messages about missing or invalid credentials
- **API errors**: Detailed error messages from Zoho CRM API
- **Network errors**: Connection and timeout error handling
- **Data validation**: Input parameter validation

All errors are returned in a consistent format:
```json
{
  "error": "Description of the error",
  "details": "Additional error details if available"
}
```

## Security Considerations

### Current Implementation (Development)
- Refresh tokens are stored in `.env` file (plain text)
- Suitable for development and testing

### Production Recommendations
- Store refresh tokens in encrypted database
- Use secure key management services (AWS KMS, Azure Key Vault, etc.)
- Implement token rotation policies
- Use environment variables for sensitive configuration
- Enable audit logging
- Implement rate limiting

## Extending the Server

To add new tools:

1. **Add the function to `zoho_mcp/zoho_tools.py`**:
   ```python
   def new_tool_function(param1: str, param2: int) -> Dict[str, Any]:
       # Implementation
       pass
   ```

2. **Create MCP tool wrapper in `zoho_mcp/server.py`**:
   ```python
   @mcp.tool()
   def new_tool(param1: str, param2: int) -> Dict[str, Any]:
       """
       Description of the new tool.
       
       Args:
           param1: Description of parameter 1
           param2: Description of parameter 2
           
       Returns:
           Description of return value
       """
       return new_tool_function(param1, param2)
   ```

3. **Update documentation**

## Troubleshooting

### Common Issues

1. **"Missing .env file" error**:
   - Create a `.env` file in your working directory
   - Copy from `.env.example` and fill in your credentials

2. **"Not authenticated" error**:
   - Run `zoho-mcp-auth` to set up authentication
   - Check that your `.env` file has valid credentials

3. **"Token refresh failed"**:
   - Re-run the OAuth setup process
   - Delete old tokens from `.env` and re-authenticate

4. **"API request failed"**:
   - Verify your Zoho CRM permissions
   - Check that the API domain is correct for your region

5. **"Contact/Deal not found"**:
   - Verify the search criteria
   - Check that the record exists in your CRM

### Environment Variable Issues

1. **Missing environment variables**:
   - Ensure `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` are set in `.env`
   - Check `.env.example` for the complete list

2. **Invalid credentials**:
   - Verify your `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET`
   - Ensure they match your Zoho Developer Console app

3. **Wrong redirect URI**:
   - Ensure `ZOHO_REDIRECT_URI` matches your Zoho app configuration
   - Default should be `http://localhost:8080/callback`

4. **Authentication flow issues**:
   - If authentication fails, delete `ZOHO_ACCESS_TOKEN` and `ZOHO_REFRESH_TOKEN` from `.env`
   - Restart the server to trigger a fresh OAuth flow

### Debug Mode

For debugging, you can add logging to see API requests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Rate Limits

Zoho CRM has API rate limits:
- Free edition: 200 API calls per day
- Paid editions: Higher limits based on plan

The server doesn't implement rate limiting, so monitor your usage accordingly.

## Support

For issues related to:
- **Zoho CRM API**: Check [Zoho CRM API documentation](https://www.zoho.com/crm/developer/docs/)
- **MCP Protocol**: Check [Model Context Protocol specification](https://modelcontextprotocol.io/)
- **This server**: Check the error messages and logs

## License

This project is provided as-is for educational and development purposes.