import requests
import logging
from typing import Optional, Dict, Any
import time
import random

class SmartProxy:
    """
    SmartProxy Residential Proxy integration - 3-day FREE trial available
    """
    
    def __init__(self, username: str, password: str, endpoint: str = "gate.decodo.com:10001"):
        self.logger = logging.getLogger(__name__)
        self.username = username
        self.password = password
        self.endpoint = endpoint
        
        # Proxy configuration
        self.proxy_config = {
            'http': f'http://{username}:{password}@{endpoint}',
            'https': f'http://{username}:{password}@{endpoint}'
        }
        
        # Browser-like headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with proxy and headers"""
        self.session = requests.Session()
        self.session.proxies.update(self.proxy_config)
        self.session.headers.update(self.headers)
        self.session.timeout = 30
        
        self.logger.info(f"✅ SmartProxy session configured: {self.endpoint}")
    
    def test_connection(self) -> bool:
        """Test proxy connection"""
        try:
            response = self.session.get('http://httpbin.org/ip', timeout=15)
            if response.status_code == 200:
                data = response.json()
                ip = data.get('origin', 'Unknown')
                self.logger.info(f"✅ SmartProxy working! IP: {ip}")
                
                # Get location
                try:
                    location_resp = self.session.get(f'http://ip-api.com/json/{ip}', timeout=10)
                    if location_resp.status_code == 200:
                        location = location_resp.json()
                        self.logger.info(f"📍 Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}")
                except:
                    pass
                
                return True
            else:
                self.logger.error(f"❌ Proxy test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Proxy connection test failed: {e}")
            return False
    
    def make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request through SmartProxy with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = random.uniform(1, 3)
                    time.sleep(delay)
                
                if 'proxies' not in kwargs:
                    kwargs['proxies'] = self.proxy_config
                
                if 'headers' in kwargs:
                    headers = (self.headers or {}).copy()
                    headers.update(kwargs['headers'] or {})
                    kwargs['headers'] = headers
                else:
                    kwargs['headers'] = self.headers or {}
                
                response = self.session.request(method, url, timeout=30, **kwargs)
                
                self.logger.debug(f"✅ {method} {url} -> {response.status_code}")
                
                # Check for Cloudflare block
                if response.status_code == 403:
                    cf_ray = response.headers.get('cf-ray')
                    if cf_ray:
                        self.logger.warning(f"⚠️ Cloudflare block detected (CF-Ray: {cf_ray}) - attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            continue
                
                return response
                
            except Exception as e:
                self.logger.error(f"❌ Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET request through proxy"""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """POST request through proxy"""
        return self.make_request('POST', url, **kwargs)
    
    def patch_py_clob_client(self):
        """Monkey patch py_clob_client to use SmartProxy"""
        try:
            import py_clob_client.client
            original_post = py_clob_client.client.post
            original_get = py_clob_client.client.get
            
            def patched_post(endpoint, headers=None, data=None):
                self.logger.debug(f"🔧 Patched POST: {endpoint} with headers={headers}, data={data}")
                response = self.post(endpoint, headers=headers, data=data)
                if response is None:
                    # Create a fake 503 response if proxy failed
                    import requests
                    fake_response = requests.Response()
                    fake_response.status_code = 503
                    fake_response._content = b'{"error": "Proxy connection failed"}'
                    return fake_response
                
                # py_clob_client expects parsed responses, not Response objects
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Handle JSON responses - parse and return dict
                    if 'application/json' in content_type:
                        try:
                            return response.json()
                        except:
                            self.logger.warning(f"🔧 Invalid JSON from POST {endpoint}: {response.text[:100]}")
                            return None
                    
                    # Handle text responses
                    return response.text
                
                # For error responses, return the Response object for debugging
                self.logger.warning(f"🔧 POST error {response.status_code}: {response.text}")
                return response
            
            def patched_get(endpoint, headers=None, data=None):
                self.logger.debug(f"🔧 Patched GET: {endpoint} with headers={headers}, data={data}")
                try:
                    response = self.get(endpoint, headers=headers, data=data)
                    self.logger.debug(f"🔧 GET response: {response}, status: {response.status_code if response else None}")
                    if response and response.status_code != 200:
                        self.logger.warning(f"🔧 Non-200 response from {endpoint}: {response.status_code} - {response.text[:200]}")
                    if response is None:
                        # Create a fake 503 response if proxy failed
                        import requests
                        fake_response = requests.Response()
                        fake_response.status_code = 503
                        fake_response._content = b'{"error": "Proxy connection failed"}'
                        return fake_response
                    
                    # py_clob_client expects parsed responses, not Response objects
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        # Handle root endpoint (get_ok)
                        if endpoint.endswith('/') and response.text.strip() == '"OK"':
                            return "OK"
                        
                        # Handle JSON responses - parse and return dict
                        if 'application/json' in content_type:
                            try:
                                return response.json()
                            except:
                                self.logger.warning(f"🔧 Invalid JSON from {endpoint}: {response.text[:100]}")
                                return None
                        
                        # Handle text responses
                        return response.text
                    
                    # For error responses, return the Response object
                    return response
                except Exception as e:
                    self.logger.error(f"🔧 GET exception: {e}")
                    raise
            
            py_clob_client.client.post = patched_post
            py_clob_client.client.get = patched_get
            
            self.logger.info("✅ py_clob_client patched to use SmartProxy")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to patch py_clob_client: {e}")
            return False


# Global instance
_smartproxy = None

def setup_smartproxy(username: str, password: str, endpoint: str = "gate.decodo.com:10001") -> bool:
    """Setup SmartProxy globally"""
    global _smartproxy
    
    try:
        _smartproxy = SmartProxy(username, password, endpoint)
        
        if not _smartproxy.test_connection():
            return False
        
        if not _smartproxy.patch_py_clob_client():
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ SmartProxy setup failed: {e}")
        return False

def get_smartproxy() -> Optional[SmartProxy]:
    """Get the global SmartProxy instance"""
    return _smartproxy 