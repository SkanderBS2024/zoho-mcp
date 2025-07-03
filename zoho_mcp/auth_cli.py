#!/usr/bin/env python3
"""
Standalone authentication CLI for Zoho CRM MCP.
This script helps users generate OAuth tokens manually.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import zoho_auth
sys.path.insert(0, str(Path(__file__).parent))

from zoho_auth import setup_oauth

def main():
    """Main entry point for the authentication CLI."""
    try:
        setup_oauth()
    except KeyboardInterrupt:
        print("\n\n❌ Authentication cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()