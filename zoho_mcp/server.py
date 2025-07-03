#!/usr/bin/env python3
"""
Zoho CRM MCP Server

A Model Context Protocol server that provides tools for interacting with Zoho CRM.
Runs in STDIO transport mode for integration with MCP clients like Claude.
"""

import sys
import json
from typing import Dict, List, Any
from fastmcp import FastMCP
from .zoho_tools import (
    get_contact_by_email,
    create_contact,
    get_deal_by_name,
    create_deal,
    update_contact,
    list_open_deals,
    get_user_info
)
from .zoho_auth import ZohoAuth

mcp = FastMCP("Zoho CRM")

@mcp.tool()
def get_contact_by_email_tool(email: str) -> Dict[str, Any]:
    """
    Get contact information by email address.
    
    Args:
        email: Email address to search for
        
    Returns:
        Contact information including ID, name, phone, and other details
    """
    return get_contact_by_email(email)


@mcp.tool()
def create_contact_tool(first_name: str, last_name: str, email: str, phone: str) -> Dict[str, Any]:
    """
    Create a new contact in Zoho CRM.
    
    Args:
        first_name: Contact's first name
        last_name: Contact's last name
        email: Contact's email address
        phone: Contact's phone number
        
    Returns:
        Created contact information with ID and status
    """
    return create_contact(first_name, last_name, email, phone)


@mcp.tool()
def get_deal_by_name_tool(deal_name: str) -> Dict[str, Any]:
    """
    Get deal information by deal name.
    
    Args:
        deal_name: Name of the deal to search for
        
    Returns:
        Deal information including ID, amount, stage, and associated contacts
    """
    return get_deal_by_name(deal_name)


@mcp.tool()
def create_deal_tool(deal_name: str, contact_id: str, stage: str, amount: float) -> Dict[str, Any]:
    """
    Create a new deal in Zoho CRM.
    
    Args:
        deal_name: Name of the deal
        contact_id: ID of the associated contact
        stage: Deal stage (e.g., 'Qualification', 'Proposal', 'Negotiation', 'Closed Won')
        amount: Deal amount in the default currency
        
    Returns:
        Created deal information with ID and status
    """
    return create_deal(deal_name, contact_id, stage, amount)


@mcp.tool()
def update_contact_tool(contact_id: str, field: str, value: str) -> Dict[str, Any]:
    """
    Update a specific field of an existing contact.
    
    Args:
        contact_id: ID of the contact to update
        field: Field name to update (e.g., 'Phone', 'Email', 'First_Name', 'Last_Name')
        value: New value for the field
        
    Returns:
        Update status and confirmation message
    """
    return update_contact(contact_id, field, value)


@mcp.tool()
def list_open_deals_tool() -> List[Dict[str, Any]]:
    """
    List all open deals (excluding closed won/lost deals).
    
    Returns:
        List of open deals with their details including name, amount, stage, and dates
    """
    return list_open_deals()


@mcp.tool()
def get_user_info_tool() -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Returns:
        User information including name, email, role, and profile details
    """
    return get_user_info()


def check_authentication():
    """
    Check if the server is properly authenticated with Zoho CRM.
    Requires tokens to be manually generated beforehand.
    """
    try:
        auth = ZohoAuth()
        
        if not auth.is_authenticated():
            print("❌ Authentication Error: Missing tokens", file=sys.stderr)
            print("", file=sys.stderr)
            print("Please set up your authentication tokens first:", file=sys.stderr)
            print("1. Generate tokens manually using the OAuth flow", file=sys.stderr)
            print("2. Add them to your .env file:", file=sys.stderr)
            print("   ZOHO_ACCESS_TOKEN=your_access_token_here", file=sys.stderr)
            print("   ZOHO_REFRESH_TOKEN=your_refresh_token_here", file=sys.stderr)
            print("", file=sys.stderr)
            print("For instructions on how to generate tokens manually, run:", file=sys.stderr)
            print("   uv run zoho-mcp-auth", file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit(1)
        
        # Test authentication by getting user info
        print("Fetching user information...", file=sys.stderr)
        user_info = get_user_info()
        
        if "error" in user_info:
            print(f"❌ Authentication test failed: {user_info['error']}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Your tokens may have expired or be invalid.", file=sys.stderr)
            print("Please regenerate your tokens and update your .env file.", file=sys.stderr)
            print("Run 'uv run zoho-mcp-auth' for instructions.", file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ Authenticated as: {user_info.get('full_name', 'Unknown User')} ({user_info.get('email', 'No email')})", file=sys.stderr)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease create a .env file with your Zoho app credentials or export them as global environnement variables:", file=sys.stderr)
        print("ZOHO_CLIENT_ID=your_client_id_here", file=sys.stderr)
        print("ZOHO_CLIENT_SECRET=your_client_secret_here", file=sys.stderr)
        print("ZOHO_ACCESS_TOKEN=your_access_token_here", file=sys.stderr)
        print("ZOHO_REFRESH_TOKEN=your_refresh_token_here", file=sys.stderr)
        print("\nFor help generating tokens, run: uv run zoho-mcp-auth", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Authentication error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point for the MCP server.
    """
    # Check authentication before starting server
    check_authentication()
    
    # Log server startup
    print("Starting Zoho CRM MCP Server in STDIO mode...", file=sys.stderr)
    print("Available tools:", file=sys.stderr)
    print("  - get_contact_by_email_tool", file=sys.stderr)
    print("  - create_contact_tool", file=sys.stderr)
    print("  - get_deal_by_name_tool", file=sys.stderr)
    print("  - create_deal_tool", file=sys.stderr)
    print("  - update_contact_tool", file=sys.stderr)
    print("  - list_open_deals_tool", file=sys.stderr)
    print("  - get_user_info_tool", file=sys.stderr)
    print("Server ready for MCP client connections.", file=sys.stderr)
    
    # Run the MCP server in STDIO mode
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()