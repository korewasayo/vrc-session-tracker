import os
import time
import requests
from requests.exceptions import HTTPError

class VRChatAPI:
    BASE_URL = "https://api.vrchat.cloud/api/1"
    
    def __init__(self, auth_cookie=None, user_agent=None, group_id=None):
        self.auth_cookie = auth_cookie or os.getenv("VRCHAT_AUTH_COOKIE")
        self.user_agent = user_agent or os.getenv("USER_AGENT", "VRCGroupMod/0.1")
        self.group_id = group_id or os.getenv("VRCHAT_GROUP_ID")
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Parse the cookie string if it starts with 'authcookie_' or just use the value directly
        cookie_val = self.auth_cookie
        if cookie_val and cookie_val.startswith("authcookie_"):
            # Usually the cookie in the browser is just the token string, but the example has 'authcookie_' prefix
            # For robustness, we will set the whole string, but VRC API expects the token value.
            pass
            
        if self.auth_cookie:
            self.session.cookies.set("auth", self.auth_cookie, domain="api.vrchat.cloud")
            
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds

    def _wait_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

    def _request(self, method, endpoint, **kwargs):
        self._wait_rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        self.last_request_time = time.time()
        
        try:
            response.raise_for_status()
        except HTTPError as e:
            # Add some context to the error if possible
            error_msg = f"HTTP Error {response.status_code} for {url}"
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_msg += f": {error_data['error']['message']}"
            except Exception:
                pass
            raise Exception(error_msg) from e
            
        return response.json()

    def verify_auth(self):
        """Verify the auth cookie is valid and return current user info."""
        if not self.auth_cookie:
            raise ValueError("No auth cookie provided.")
        return self._request("GET", "/auth/user")

    def get_group_info(self):
        """Get information about the configured group."""
        if not self.group_id:
            raise ValueError("No group ID configured.")
        return self._request("GET", f"/groups/{self.group_id}")
