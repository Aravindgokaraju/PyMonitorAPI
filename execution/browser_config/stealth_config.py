import os
import tempfile
from .base_config import BaseConfig
import random
from selenium_stealth import stealth
import undetected_chromedriver as uc  # Add this import


class StealthConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)..."
        ]
        self.proxies = ["12.34.56.78:8080", "23.45.67.89:3128"]
    
    def create_driver(self):
        """Main method to create and configure the driver"""
        # Apply all chrome options
        self.apply()
        
        # Initialize undetected-chromedriver with our options
        driver = uc.Chrome(
            options=self.chrome_options,
            headless=False,
            use_subprocess=True,
            version_main=114  # Optional: specify Chrome version
        )
        
        # Apply all stealth measures
        self._apply_stealth_measures(driver)
        
        return driver
    def apply(self):
        # Apply base configurations first
        super().apply()
        
        # Advanced stealth settings
        self.chrome_options.add_argument("--disable-3d-apis")
        self.chrome_options.add_argument("--disable-webgl")
        self.chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
        self.chrome_options.add_argument("--disable-renderer-backgrounding")
        self.chrome_options.add_argument("--disable-background-timer-throttling")
        
        # Random proxy and user agent

        raw_proxy = random.choice(self.proxies)  # "ip:port"
        ip, port = raw_proxy.split(":")
        # Use random user/pass — change this if you have fixed credentials
        username = f"user-{random.randint(1000,9999)}"
        password = "pass"

        # Store proxy string for Chrome
        self.proxy_auth = {
            'proxy': {
                'http': f"http://{username}:{password}@{ip}:{port}",
                'https': f"https://{username}:{password}@{ip}:{port}",
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
        proxy_url = f"http://{username}:{password}@{ip}:{port}"
        self.chrome_options.add_argument(f'--proxy-server={proxy_url}')
        self.chrome_options.add_argument(f"user-agent={random.choice(self.user_agents)}")

        profile_path = self.create_temp_profile()
        self.chrome_options.add_argument(f"--user-data-dir={profile_path}")

        self.chrome_options.add_argument("--use-gl=desktop")
        self.chrome_options.add_argument("--ignore-gpu-blocklist")
        
        return self.chrome_options
    
   

    def create_temp_profile(self):
        profile_path = tempfile.mkdtemp()
        os.makedirs(f"{profile_path}/Default/Cache", exist_ok=True)
        os.makedirs(f"{profile_path}/Default/Cookies", exist_ok=True)
        self.profile_path = profile_path
        return profile_path
    
    def add_mouse_movement_entropy(self, driver):
        driver.execute_script("""
            const originalMove = MouseEvent.prototype.move;
            MouseEvent.prototype.move = function() {
                const event = originalMove.apply(this, arguments);
                event.movementX += Math.random() * 3 - 1.5;
                event.movementY += Math.random() * 3 - 1.5;
                return event;
            };
        """)
    def get_additional_scripts(self):
        """Return additional JavaScript strings to execute post-launch."""
        return [
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """,
            """
            Object.defineProperty(navigator, 'permissions', {
                value: {
                    query: (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            window.navigator.permissions.query(parameters)
                    )
                }
            });
            """
        ]
    #Post browser launch measures
    def _apply_stealth_measures(self,driver):
        
        # TODO: FInd Additional scripts that are not included with the selenium stuff and run them if reccommended
        for script in self.get_additional_scripts():
            self.driver.execute_script(script) 

        
        # Add mouse entropy if needed
        self.add_mouse_movement_entropy(driver)