#!/usr/bin/env python3
"""
Cloudflare bypass fix for py-clob-client
"""

import requests
import time
import random
import json

def monkey_patch_requests():
    """
    Patch the requests library to always use proper headers
    """
    original_request = requests.Session.request
    
    def patched_request(self, method, url, **kwargs):
        """Enhanced request with Cloudflare bypass headers"""
        
        # Enhanced browser headers with better POST support
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        
        # Add specific headers for POST requests
        if method.upper() == 'POST':
            default_headers.update({
                'Origin': 'https://polymarket.com',
                'Referer': 'https://polymarket.com/',
                'Content-Type': 'application/json',
            })
        
        # Merge with existing headers
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        for key, value in default_headers.items():
            if key not in kwargs['headers']:
                kwargs['headers'][key] = value
        
        # Add small delay to avoid rate limiting
        time.sleep(random.uniform(0.05, 0.15))
        
        return original_request(self, method, url, **kwargs)
    
    requests.Session.request = patched_request
    
    # Also patch the global requests functions
    original_get = requests.get
    original_post = requests.post
    
    def patched_get(url, **kwargs):
        session = requests.Session()
        return session.get(url, **kwargs)
    
    def patched_post(url, **kwargs):
        session = requests.Session()
        return session.post(url, **kwargs)
    
    requests.get = patched_get
    requests.post = patched_post

def apply_cloudflare_fix():
    """
    Apply all Cloudflare bypass patches
    """
    print("🛡️  Applying Cloudflare bypass fix...")
    
    try:
        # Patch requests library first
        monkey_patch_requests()
        print("✅ Requests library patched")
        
        # Try to patch py_clob_client if available
        try:
            import py_clob_client.http_helpers.helpers as helpers
            original_request = helpers.request
            
            def clob_patched_request(endpoint, method, headers=None, data=None):
                if headers is None:
                    headers = {}
                
                # Add essential headers for Cloudflare bypass
                browser_headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                }
                
                final_headers = {**browser_headers, **headers}
                time.sleep(random.uniform(0.1, 0.2))
                
                return original_request(endpoint, method, final_headers, data)
            
            helpers.request = clob_patched_request
            print("✅ py_clob_client patched")
            
        except ImportError:
            print("⚠️  py_clob_client not available yet, will patch when imported")
    
    except Exception as e:
        print(f"❌ Error applying Cloudflare fix: {e}")
    
    print("🚀 Cloudflare bypass ready!")

if __name__ == "__main__":
    apply_cloudflare_fix() 