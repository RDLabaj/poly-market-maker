import requests
import json
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class FlareSolverrClient:
    """
    Klient do obejścia Cloudflare używając FlareSolverr
    """
    
    def __init__(self, flaresolverr_url: str = "http://localhost:8191"):
        self.flaresolverr_url = flaresolverr_url
        self.session_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Wysyła request do FlareSolverr"""
        url = urljoin(self.flaresolverr_url, "/v1")
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def create_session(self, target_url: str) -> str:
        """Tworzy nową sesję FlareSolverr"""
        payload = {
            "cmd": "sessions.create",
            "url": target_url,
            "maxTimeout": 60000
        }
        
        response = self._send_request(payload)
        
        if response.get("status") == "ok":
            self.session_id = response["session"]
            self.logger.info(f"FlareSolverr session created: {self.session_id}")
            return self.session_id
        else:
            raise Exception(f"Failed to create session: {response}")
    
    def destroy_session(self) -> bool:
        """Niszczy aktualną sesję"""
        if not self.session_id:
            return True
            
        payload = {
            "cmd": "sessions.destroy",
            "session": self.session_id
        }
        
        try:
            response = self._send_request(payload)
            if response.get("status") == "ok":
                self.logger.info(f"Session {self.session_id} destroyed")
                self.session_id = None
                return True
        except Exception as e:
            self.logger.error(f"Failed to destroy session: {e}")
        
        return False
    
    def get_cookies_and_headers(self, url: str) -> Dict[str, Any]:
        """Pobiera cookies i headers po przejściu przez Cloudflare"""
        
        # Jeśli nie ma sesji, stwórz nową
        if not self.session_id:
            self.create_session(url)
        
        payload = {
            "cmd": "request.get",
            "url": url,
            "session": self.session_id,
            "maxTimeout": 60000
        }
        
        response = self._send_request(payload)
        
        if response.get("status") == "ok":
            solution = response["solution"]
            
            # Konwertuj cookies do formatu dla requests
            cookies_dict = {}
            if "cookies" in solution:
                for cookie in solution["cookies"]:
                    cookies_dict[cookie["name"]] = cookie["value"]
            
            return {
                "cookies": cookies_dict,
                "user_agent": solution.get("userAgent", ""),
                "response": solution.get("response", "")
            }
        else:
            raise Exception(f"Failed to get cookies: {response}")
    
    def post_with_cloudflare_bypass(self, url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> requests.Response:
        """Wykonuje POST request z obejściem Cloudflare"""
        
        # Najpierw pobierz cookies
        try:
            cf_data = self.get_cookies_and_headers(url)
            cookies = cf_data["cookies"]
            user_agent = cf_data["user_agent"]
            
            # Przygotuj headers
            request_headers = {
                "User-Agent": user_agent,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://clob.polymarket.com",
                "Referer": "https://clob.polymarket.com/",
            }
            
            if headers:
                request_headers.update(headers)
            
            # Wykonaj POST request z cookies
            response = requests.post(
                url,
                json=data,
                headers=request_headers,
                cookies=cookies,
                timeout=30
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"POST request failed: {e}")
            raise


class CloudflareBypassMonkeyPatch:
    """
    Monkey patch dla py_clob_client żeby używał FlareSolverr
    """
    
    def __init__(self):
        self.flaresolverr = FlareSolverrClient()
        self.logger = logging.getLogger(__name__)
        
    def apply_patch(self):
        """Zastępuje POST requesty w py_clob_client"""
        import py_clob_client.http_helpers.helpers as http_helpers
        
        # Zachowaj oryginalne funkcje
        original_post = http_helpers.post
        original_request = http_helpers.request
        
        def patched_post(endpoint: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None):
            """Zastąpiona funkcja POST używająca FlareSolverr"""
            self.logger.debug(f"FlareSolverr POST to: {endpoint}")
            
            try:
                response = self.flaresolverr.post_with_cloudflare_bypass(
                    url=endpoint,
                    data=data,
                    headers=headers
                )
                
                # Zwróć response w formacie oczekiwanym przez py_clob_client
                return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                
            except Exception as e:
                self.logger.error(f"FlareSolverr POST failed: {e}")
                # Fallback do oryginalnej funkcji
                return original_post(endpoint, headers, data)
        
        def patched_request(endpoint: str, method: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None):
            """Zastąpiona funkcja request"""
            if method.upper() == "POST":
                return patched_post(endpoint, headers, data)
            else:
                # GET requesty działają, zostaw bez zmian
                return original_request(endpoint, method, headers, data)
        
        # Zastąp funkcje
        http_helpers.post = patched_post
        http_helpers.request = patched_request
        
        self.logger.info("FlareSolverr monkey patch applied successfully")


def setup_flaresolverr_bypass():
    """
    Główna funkcja do uruchomienia obejścia Cloudflare
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Sprawdź czy FlareSolverr działa
        flaresolverr = FlareSolverrClient()
        response = requests.get("http://localhost:8191", timeout=5)
        if response.status_code == 200:
            logger.info("FlareSolverr is running, applying bypass...")
            
            # Zastosuj monkey patch
            bypass = CloudflareBypassMonkeyPatch()
            bypass.apply_patch()
            
            return True
        else:
            logger.error("FlareSolverr not responding")
            return False
            
    except Exception as e:
        logger.error(f"Failed to setup FlareSolverr bypass: {e}")
        return False


if __name__ == "__main__":
    # Test FlareSolverr
    setup_flaresolverr_bypass() 