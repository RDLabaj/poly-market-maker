import requests
import json
import logging
from typing import Optional, Dict, Any

class CloudFreedClient:
    """
    Klient do obejścia Cloudflare używając CloudFreed API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.cloudfreed.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
    def bypass_cloudflare_post(self, url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> requests.Response:
        """
        Wykonuje POST request z obejściem Cloudflare przez CloudFreed
        """
        
        payload = {
            "url": url,
            "method": "POST",
            "headers": headers or {},
            "body": json.dumps(data),
            "format": "json"
        }
        
        cloudfreed_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/solve",
                headers=cloudfreed_headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                # CloudFreed zwraca response w formacie JSON
                response_data = result.get("data", {})
                
                # Stwórz mock response object
                mock_response = MockResponse(
                    status_code=response_data.get("status", 200),
                    content=response_data.get("body", ""),
                    headers=response_data.get("headers", {})
                )
                
                return mock_response
            else:
                raise Exception(f"CloudFreed request failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"CloudFreed POST request failed: {e}")
            raise


class MockResponse:
    """Mock response object dla CloudFreed"""
    
    def __init__(self, status_code: int, content: str, headers: Dict[str, str]):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.text = content
        
    def json(self):
        return json.loads(self.content) if self.content else {}
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def setup_cloudfreed_bypass(api_key: str):
    """
    Ustawia CloudFreed jako bypass dla Cloudflare
    """
    logger = logging.getLogger(__name__)
    
    try:
        import py_clob_client.http_helpers.helpers as http_helpers
        
        # Zachowaj oryginalne funkcje
        original_post = http_helpers.post
        original_request = http_helpers.request
        
        # Stwórz klienta CloudFreed
        cloudfreed = CloudFreedClient(api_key)
        
        def patched_post(endpoint: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None):
            """Zastąpiona funkcja POST używająca CloudFreed"""
            logger.debug(f"CloudFreed POST to: {endpoint}")
            
            try:
                response = cloudfreed.bypass_cloudflare_post(
                    url=endpoint,
                    data=data,
                    headers=headers
                )
                
                return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                
            except Exception as e:
                logger.error(f"CloudFreed POST failed: {e}")
                # Fallback do oryginalnej funkcji
                return original_post(endpoint, headers, data)
        
        def patched_request(endpoint: str, method: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None):
            """Zastąpiona funkcja request"""
            if method.upper() == "POST":
                return patched_post(endpoint, headers, data)
            else:
                return original_request(endpoint, method, headers, data)
        
        # Zastąp funkcje
        http_helpers.post = patched_post
        http_helpers.request = patched_request
        
        logger.info("CloudFreed bypass applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup CloudFreed bypass: {e}")
        return False


if __name__ == "__main__":
    # Test
    api_key = input("Enter CloudFreed API key: ")
    setup_cloudfreed_bypass(api_key) 