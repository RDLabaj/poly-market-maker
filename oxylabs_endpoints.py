"""
Oxylabs residential proxy endpoints configuration
Different endpoints for different regions and use cases
"""

# Main residential proxy endpoints
OXYLABS_ENDPOINTS = {
    # Standard residential endpoints
    "residential_global": "residential.oxylabs.io:8001",
    "residential_us": "us-pr.oxylabs.io:10000", 
    "residential_eu": "pr.oxylabs.io:8001",
    
    # Sticky session endpoints (better for Cloudflare)
    "sticky_global": "residential.oxylabs.io:8001",
    "sticky_us": "us-pr.oxylabs.io:40000",
    "sticky_eu": "pr.oxylabs.io:40000",
    
    # High-performance endpoints  
    "premium_us": "us-pr.oxylabs.io:20000",
    "premium_eu": "pr.oxylabs.io:20000",
}

# Recommended endpoint priority for Polymarket (US-based service)
POLYMARKET_PRIORITY = [
    "sticky_us",       # Best for Cloudflare bypass
    "premium_us",      # High performance US
    "residential_us",  # Standard US
    "sticky_global",   # Global fallback
    "residential_global"  # Last resort
]

# Custom headers for each region
REGION_HEADERS = {
    "us": {
        'Accept-Language': 'en-US,en;q=0.9',
        'CF-IPCountry': 'US',
        'CF-Connecting-IP': None,  # Will be set automatically
    },
    "eu": {
        'Accept-Language': 'en-GB,en;q=0.9',
        'CF-IPCountry': 'GB',
        'CF-Connecting-IP': None,
    },
    "global": {
        'Accept-Language': 'en-US,en;q=0.9',
        'CF-IPCountry': 'US',
    }
}

def get_recommended_endpoint(service: str = "polymarket") -> str:
    """Get recommended endpoint for specific service"""
    if service.lower() == "polymarket":
        return OXYLABS_ENDPOINTS[POLYMARKET_PRIORITY[0]]
    return OXYLABS_ENDPOINTS["residential_global"]

def get_all_endpoints_for_testing() -> list:
    """Get all endpoints for testing in priority order"""
    return [OXYLABS_ENDPOINTS[key] for key in POLYMARKET_PRIORITY]

def get_region_from_endpoint(endpoint: str) -> str:
    """Extract region from endpoint"""
    if "us-pr" in endpoint:
        return "us"
    elif "pr.oxylabs" in endpoint and "us-pr" not in endpoint:
        return "eu"
    else:
        return "global" 