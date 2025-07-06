import requests
from typing import Dict, List, Optional, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)


class PluggyError(Exception):
    """Custom exception for Pluggy API errors"""
    pass


class PluggyClient:
    """Client for interacting with Pluggy API"""

    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.base_url = "https://api.sandbox.pluggy.ai" if sandbox else "https://api.pluggy.ai"
        self.api_key: Optional[str] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.api_key:
            raise PluggyError("Authentication required. Call authenticate() first.")
        
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise errors if necessary"""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", "Unknown error")
            except:
                message = f"HTTP {response.status_code} error"
            
            if response.status_code == 401:
                raise PluggyError(f"Authentication failed: {message}")
            else:
                raise PluggyError(f"API error: {message}")
        
        return response.json()

    def authenticate(self) -> None:
        """Authenticate with Pluggy API and obtain API key"""
        url = f"{self.base_url}/auth"
        data = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=data, headers=headers)
        result = self._handle_response(response)
        
        self.api_key = result.get("apiKey")
        if not self.api_key:
            raise PluggyError("Failed to obtain API key from authentication response")

    def get_connectors(self, **params) -> List[Dict[str, Any]]:
        """Get available bank connectors"""
        url = f"{self.base_url}/connectors"
        headers = self._get_headers()
        
        if params:
            response = requests.get(url, headers=headers, params=params)
        else:
            response = requests.get(url, headers=headers)
        result = self._handle_response(response)
        
        return result.get("results", [])

    def create_item(self, connector_id: str, parameters: Dict[str, str]) -> Dict[str, Any]:
        """Create a new connection item"""
        url = f"{self.base_url}/items"
        headers = self._get_headers()
        data = {
            "connectorId": connector_id,
            "parameters": parameters
        }
        
        response = requests.post(url, json=data, headers=headers)
        return self._handle_response(response)

    def get_item_status(self, item_id: str) -> Dict[str, Any]:
        """Get status of an item connection"""
        url = f"{self.base_url}/items/{item_id}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return self._handle_response(response)

    def get_accounts(self, item_id: str) -> List[Dict[str, Any]]:
        """Get accounts for an item"""
        url = f"{self.base_url}/accounts"
        headers = self._get_headers()
        params = {"itemId": item_id}
        
        response = requests.get(url, headers=headers, params=params)
        result = self._handle_response(response)
        
        return result.get("results", [])

    def get_transactions(
        self, 
        account_id: str, 
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        **params
    ) -> List[Dict[str, Any]]:
        """Get transactions for an account"""
        url = f"{self.base_url}/transactions"
        headers = self._get_headers()
        
        query_params = {"accountId": account_id}
        if from_date:
            query_params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            query_params["to"] = to_date.strftime("%Y-%m-%d")
        query_params.update(params)
        
        response = requests.get(url, headers=headers, params=query_params)
        result = self._handle_response(response)
        
        return result.get("results", [])

    def delete_item(self, item_id: str) -> None:
        """Delete an item connection"""
        url = f"{self.base_url}/items/{item_id}"
        headers = self._get_headers()
        
        response = requests.delete(url, headers=headers)
        # For DELETE, we just check for errors
        if response.status_code >= 400:
            self._handle_response(response)

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get available transaction categories"""
        url = f"{self.base_url}/categories"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        result = self._handle_response(response)
        
        return result.get("results", [])