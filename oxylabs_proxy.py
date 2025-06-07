import requests
import logging
from typing import Optional, Dict, Any
import time
import random
from urllib.parse import urljoin
from oxylabs_endpoints import get_recommended_endpoint, get_region_from_endpoint, REGION_HEADERS

class OxylabsProxy:
    """
    Oxylabs Residential Proxy integration for bypassing Cloudflare protection
    """
    
    def __init__(self, username: str, password: str, endpoint: str = None):
        self.logger = logging.getLogger(__name__)
        self.username = username
        self.password = password
        
        # Use recommended endpoint if none provided
        if endpoint is None:
            endpoint = get_recommended_endpoint("polymarket")
        self.endpoint = endpoint
        
        # Get region-specific headers
        region = get_region_from_endpoint(endpoint)
        region_headers = REGION_HEADERS.get(region, REGION_HEADERS["global"])
        
        # Proxy configuration
        self.proxy_config = {
            'http': f'http://{username}:{password}@{endpoint}',
            'https': f'http://{username}:{password}@{endpoint}'
        }
        
        # Browser-like headers to mimic real user (with region-specific tweaks)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Add region-specific headers
        self.headers.update(region_headers)
        
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with proxy and headers"""
        self.session = requests.Session()
        self.session.proxies.update(self.proxy_config)
        self.session.headers.update(self.headers)
        
        # Set timeouts
        self.session.timeout = 30
        
        self.logger.info(f"✅ Oxylabs proxy session configured: {self.endpoint}")
    
    def test_connection(self) -> bool:
        """Test proxy connection and IP location"""
        try:
            # Test with whatismyipaddress.com
            response = self.session.get('https://whatismyipaddress.com/api/ip.php', timeout=15)
            if response.status_code == 200:
                ip = response.text.strip()
                self.logger.info(f"✅ Oxylabs proxy working! IP: {ip}")
                
                # Get location info
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
        """
        Make HTTP request through Oxylabs proxy with retry logic
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid being flagged
                if attempt > 0:
                    delay = random.uniform(1, 3)
                    time.sleep(delay)
                
                # Ensure we're using the proxy session
                if 'proxies' not in kwargs:
                    kwargs['proxies'] = self.proxy_config
                
                # Merge headers
                if 'headers' in kwargs:
                    headers = self.headers.copy()
                    headers.update(kwargs['headers'])
                    kwargs['headers'] = headers
                else:
                    kwargs['headers'] = self.headers
                
                # Make request
                response = self.session.request(method, url, timeout=30, **kwargs)
                
                # Log successful request
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
        """
        Monkey patch py_clob_client to use Oxylabs proxy
        """
        try:
            import py_clob_client.http_helpers
            original_post = py_clob_client.http_helpers.post
            original_get = py_clob_client.http_helpers.get
            
            def patched_post(url, data=None, json=None, headers=None, **kwargs):
                self.logger.debug(f"🔧 Patched POST: {url}")
                return self.post(url, data=data, json=json, headers=headers, **kwargs)
            
            def patched_get(url, headers=None, **kwargs):
                self.logger.debug(f"🔧 Patched GET: {url}")
                return self.get(url, headers=headers, **kwargs)
            
            py_clob_client.http_helpers.post = patched_post
            py_clob_client.http_helpers.get = patched_get
            
            self.logger.info("✅ py_clob_client patched to use Oxylabs proxy")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to patch py_clob_client: {e}")
            return False


# Singleton instance
_oxylabs_proxy = None

def setup_oxylabs_proxy(username: str, password: str, endpoint: str = "residential.oxylabs.io:8001") -> bool:
    """
    Setup Oxylabs proxy globally
    """
    global _oxylabs_proxy
    
    try:
        _oxylabs_proxy = OxylabsProxy(username, password, endpoint)
        
        # Test connection
        if not _oxylabs_proxy.test_connection():
            return False
        
        # Patch py_clob_client
        if not _oxylabs_proxy.patch_py_clob_client():
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Oxylabs setup failed: {e}")
        return False

def get_oxylabs_proxy() -> Optional[OxylabsProxy]:
    """Get the global Oxylabs proxy instance"""
    return _oxylabs_proxy 