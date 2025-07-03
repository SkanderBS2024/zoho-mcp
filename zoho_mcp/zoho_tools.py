import json
import requests
from typing import Dict, List, Any, Optional
from .zoho_auth import ZohoAuth


class ZohoTools:
    """Zoho CRM API tools for MCP server."""
    
    def __init__(self):
        self.auth = ZohoAuth()
        self.api_base = f"{self.auth.api_domain}/crm/v2"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Zoho CRM."""
        try:
            print(f"Getting auth headers...")
            headers = self.auth.get_auth_headers()
            print(f"Auth headers obtained")
            
            url = f"{self.api_base}/{endpoint}"
            print(f"Making {method} request to: {url}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            print(f"Exception in _make_request: {e}")
            return {"error": f"Request failed: {str(e)}"}
    
    def get_contact_by_email(self, email: str) -> Dict[str, Any]:
        """Get contact information by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Dict containing contact information or error message
        """
        print(f"Searching for contact with email: {email}")
        
        # Search contacts by email
        search_params = {
            "criteria": f"Email:equals:{email}"
        }
        
        result = self._make_request("GET", "Contacts/search", search_params)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        if not data:
            return {"error": "Contact not found"}
        
        # Return the first matching contact
        contact = data[0]
        return {
            "id": contact.get("id"),
            "first_name": contact.get("First_Name"),
            "last_name": contact.get("Last_Name"),
            "email": contact.get("Email"),
            "phone": contact.get("Phone"),
            "account_name": contact.get("Account_Name", {}).get("name") if contact.get("Account_Name") else None,
            "created_time": contact.get("Created_Time"),
            "modified_time": contact.get("Modified_Time")
        }
    
    def create_contact(self, first_name: str, last_name: str, email: str, phone: str) -> Dict[str, Any]:
        """Create a new contact in Zoho CRM.
        
        Args:
            first_name: Contact's first name
            last_name: Contact's last name
            email: Contact's email address
            phone: Contact's phone number
            
        Returns:
            Dict containing created contact information or error message
        """
        print(f"Creating contact: {first_name} {last_name} ({email})")
        
        contact_data = {
            "data": [{
                "First_Name": first_name,
                "Last_Name": last_name,
                "Email": email,
                "Phone": phone
            }]
        }
        
        result = self._make_request("POST", "Contacts", contact_data)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        if not data:
            return {"error": "Failed to create contact"}
        
        created_contact = data[0]
        if created_contact.get("status") == "success":
            return {
                "id": created_contact.get("details", {}).get("id"),
                "status": "success",
                "message": "Contact created successfully"
            }
        else:
            return {
                "error": "Failed to create contact",
                "details": created_contact
            }
    
    def get_deal_by_name(self, deal_name: str) -> Dict[str, Any]:
        """Get deal information by deal name.
        
        Args:
            deal_name: Name of the deal to search for
            
        Returns:
            Dict containing deal information or error message
        """
        print(f"Searching for deal: {deal_name}")
        
        search_params = {
            "criteria": f"Deal_Name:equals:{deal_name}"
        }
        
        result = self._make_request("GET", "Deals/search", search_params)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        if not data:
            return {"error": "Deal not found"}
        
        deal = data[0]
        return {
            "id": deal.get("id"),
            "deal_name": deal.get("Deal_Name"),
            "amount": deal.get("Amount"),
            "stage": deal.get("Stage"),
            "contact_name": deal.get("Contact_Name", {}).get("name") if deal.get("Contact_Name") else None,
            "account_name": deal.get("Account_Name", {}).get("name") if deal.get("Account_Name") else None,
            "closing_date": deal.get("Closing_Date"),
            "created_time": deal.get("Created_Time"),
            "modified_time": deal.get("Modified_Time")
        }
    
    def create_deal(self, deal_name: str, contact_id: str, stage: str, amount: float) -> Dict[str, Any]:
        """Create a new deal in Zoho CRM.
        
        Args:
            deal_name: Name of the deal
            contact_id: ID of the associated contact
            stage: Deal stage (e.g., 'Qualification', 'Proposal', 'Closed Won')
            amount: Deal amount
            
        Returns:
            Dict containing created deal information or error message
        """
        print(f"Creating deal: {deal_name} (${amount})")
        
        deal_data = {
            "data": [{
                "Deal_Name": deal_name,
                "Contact_Name": contact_id,
                "Stage": stage,
                "Amount": amount
            }]
        }
        
        result = self._make_request("POST", "Deals", deal_data)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        if not data:
            return {"error": "Failed to create deal"}
        
        created_deal = data[0]
        if created_deal.get("status") == "success":
            return {
                "id": created_deal.get("details", {}).get("id"),
                "status": "success",
                "message": "Deal created successfully"
            }
        else:
            return {
                "error": "Failed to create deal",
                "details": created_deal
            }
    
    def update_contact(self, contact_id: str, field: str, value: str) -> Dict[str, Any]:
        """Update a specific field of a contact.
        
        Args:
            contact_id: ID of the contact to update
            field: Field name to update (e.g., 'Phone', 'Email', 'First_Name')
            value: New value for the field
            
        Returns:
            Dict containing update status or error message
        """
        print(f"Updating contact {contact_id}: {field} = {value}")
        
        update_data = {
            "data": [{
                "id": contact_id,
                field: value
            }]
        }
        
        result = self._make_request("PUT", "Contacts", update_data)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        if not data:
            return {"error": "Failed to update contact"}
        
        updated_contact = data[0]
        if updated_contact.get("status") == "success":
            return {
                "status": "success",
                "message": f"Contact {field} updated successfully"
            }
        else:
            return {
                "error": "Failed to update contact",
                "details": updated_contact
            }
    
    def list_open_deals(self) -> List[Dict[str, Any]]:
        """List all open deals (not closed won/lost).
        
        Returns:
            List of open deals or error message
        """
        print("Fetching open deals...")
        
        # Get deals that are not in closed stages
        search_params = {
            "criteria": "(Stage:not_equal:Closed Won)and(Stage:not_equal:Closed Lost)"
        }
        
        result = self._make_request("GET", "Deals/search", search_params)
        
        if "error" in result:
            return result
        
        data = result.get("data", [])
        
        open_deals = []
        for deal in data:
            open_deals.append({
                "id": deal.get("id"),
                "deal_name": deal.get("Deal_Name"),
                "amount": deal.get("Amount"),
                "stage": deal.get("Stage"),
                "contact_name": deal.get("Contact_Name", {}).get("name") if deal.get("Contact_Name") else None,
                "account_name": deal.get("Account_Name", {}).get("name") if deal.get("Account_Name") else None,
                "closing_date": deal.get("Closing_Date"),
                "created_time": deal.get("Created_Time")
            })
        
        return open_deals
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information.
        
        Returns:
            Dict containing user information or error message
        """
        try:
            print("Fetching user information...")
            print("Making API request to get user info...")
            
            result = self._make_request("GET", "users?type=CurrentUser")
            print(f"API response received: {result is not None}")
            
            if "error" in result:
                print(f"Error in API response: {result['error']}")
                return result
            
            users = result.get("users", [])
            if not users:
                print("No user data in response")
                return {"error": "User information not found"}
            
            print("User info retrieved successfully")
            user = users[0]
            return {
                "id": user.get("id"),
                "full_name": user.get("full_name"),
                "email": user.get("email"),
                "role": user.get("role", {}).get("name") if user.get("role") else None,
                "profile": user.get("profile", {}).get("name") if user.get("profile") else None,
                "status": user.get("status"),
                "time_zone": user.get("time_zone")
            }
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {"error": f"Exception occurred: {str(e)}"}


# Tool function wrappers for MCP
def get_contact_by_email(email: str) -> Dict[str, Any]:
    """MCP tool: Get contact by email address."""
    tools = ZohoTools()
    return tools.get_contact_by_email(email)


def create_contact(first_name: str, last_name: str, email: str, phone: str) -> Dict[str, Any]:
    """MCP tool: Create a new contact."""
    tools = ZohoTools()
    return tools.create_contact(first_name, last_name, email, phone)


def get_deal_by_name(deal_name: str) -> Dict[str, Any]:
    """MCP tool: Get deal by name."""
    tools = ZohoTools()
    return tools.get_deal_by_name(deal_name)


def create_deal(deal_name: str, contact_id: str, stage: str, amount: float) -> Dict[str, Any]:
    """MCP tool: Create a new deal."""
    tools = ZohoTools()
    return tools.create_deal(deal_name, contact_id, stage, amount)


def update_contact(contact_id: str, field: str, value: str) -> Dict[str, Any]:
    """MCP tool: Update a contact field."""
    tools = ZohoTools()
    return tools.update_contact(contact_id, field, value)


def list_open_deals() -> List[Dict[str, Any]]:
    """MCP tool: List all open deals."""
    tools = ZohoTools()
    return tools.list_open_deals()


def get_user_info() -> Dict[str, Any]:
    """MCP tool: Get current user information."""
    tools = ZohoTools()
    return tools.get_user_info()