import os
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from dotenv import load_dotenv


class ZohoAuth:
    """Handles Zoho OAuth2 authentication and token management using environment variables."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.base_url = "https://accounts.zoho.com/oauth/v2"
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
        
        # Required OAuth credentials
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "http://localhost:8080/callback")
        self.scope = os.getenv("ZOHO_SCOPE", "ZohoCRM.modules.ALL,ZohoCRM.users.READ")
        
        # Authentication tokens
        self.access_token = os.getenv("ZOHO_ACCESS_TOKEN")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        
        # Validate required credentials
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing required environment variables: ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET. "
                "Please check your .env file or environment variables."
            )
    
    def _update_env_file(self, key: str, value: str) -> None:
        """Update a specific key in the .env file (deprecated - for manual token generation only)."""
        # This method is kept for backward compatibility but should not be used in production
        # Tokens should be manually set in environment variables
        pass
    
    def generate_auth_url(self) -> str:
        """Generate OAuth authorization URL for user consent."""
        params = {
            "scope": self.scope,
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "access_type": "offline"
        }
        
        auth_url = f"{self.base_url}/auth?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        token_url = f"{self.base_url}/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def refresh_access_token(self) -> str:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            raise Exception("No refresh token available. Please re-authenticate.")
        
        token_url = f"{self.base_url}/token"
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Update access token in memory only
            self.access_token = token_data.get("access_token", "")
            
            return self.access_token
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self.access_token:
            if self.refresh_token:
                return self.refresh_access_token()
            else:
                raise Exception("No access token or refresh token available. Please authenticate.")
        
        # Return the existing access token if we have one
        # In a production environment, you would check token expiry time here
        return self.access_token
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        access_token = self.get_valid_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication credentials."""
        return bool(self.refresh_token or self.access_token)


def setup_oauth():
    """Helper function to generate OAuth tokens manually."""
    try:
        auth = ZohoAuth()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease create a .env file with your Zoho app credentials or export then as global environnement variables:")
        print("ZOHO_CLIENT_ID=your_client_id_here")
        print("ZOHO_CLIENT_SECRET=your_client_secret_here")
        return
    
    print("🔐 Zoho CRM Manual Token Generation")
    print("===================================\n")
    
    if auth.is_authenticated():
        print("✓ Tokens already configured in environment variables!")
        print("\nIf you need to regenerate tokens, remove ZOHO_ACCESS_TOKEN and ZOHO_REFRESH_TOKEN from your .env file first.")
        return
    
    # Generate auth URL
    auth_url = auth.generate_auth_url()
    print("Step 1: Visit the authorization URL")
    print("====================================")
    print(f"Please visit this URL to authorize the application:\n")
    print(auth_url)
    print("\nStep 2: Get the authorization code")
    print("==================================")
    print("After authorization, you'll be redirected to your redirect_uri.")
    print("Copy the 'code' parameter from the redirect URL and paste it below.")
    
    code = input("\nEnter authorization code: ").strip()
    
    try:
        tokens = auth.exchange_code_for_tokens(code)
        print("\n✅ Token generation successful!")
        print("\nStep 3: Add tokens to your .env file")
        print("====================================")
        print("Add the following lines to your environnement variables before launching the server:\n")
        print(f"ZOHO_ACCESS_TOKEN={tokens.get('access_token', '')}")
        print(f"ZOHO_REFRESH_TOKEN={tokens.get('refresh_token', '')}")
        print("\n⚠️  Important: Keep these tokens secure and never commit them to version control!")
        print("\nAfter adding the tokens to your .env file, you can run the MCP server with:")
        print("uv run zoho-mcp")
    except Exception as e:
        print(f"\n❌ Token generation failed: {e}")
        print("Please check your authorization code and try again.")


if __name__ == "__main__":
    setup_oauth()