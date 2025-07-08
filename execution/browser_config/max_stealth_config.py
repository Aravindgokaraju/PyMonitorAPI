import os
import tempfile
import time

from execution.browser_config.browser import Browser
from .base_config import BaseConfig
import random
from selenium_stealth import stealth


class MaxStealthConfig(BaseConfig):
    def __init__(self):
        super().__init__()

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)..."
        ]
        self.proxies = ["12.34.56.78:8080", "23.45.67.89:3128"]
    
    def create_driver(self):
        """Main method to create and configure the driver"""
        uc = Browser.get_uc()  # Lazy load happens here
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
        # self.chrome_options.add_argument('--timezone=America/New_York') # TODO: is this better or cdp script


        
        # Random proxy and user agent 

        raw_proxy = random.choice(self.proxies)  # "ip:port"
        ip, port = raw_proxy.split(":")
        # Use random user/pass — change this if you have fixed credentials
        # TODO: strenghten proxy cred security
        base_user = os.getenv("PROXY_USER", "default_user")  # 2nd arg = optional fallback
        username = f"{base_user}-{random.randint(1000,9999)}"

        password = os.getenv("PROXY_PASS")  # No fallback = fails if missing

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
    

    def get_cdp_scripts(self):
        """Return CDP scripts for stealth configuration"""
        canvas_script = """
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(0, 0, 100, 100);
        ctx.fillStyle = '#069';
        ctx.fillText('Hello World', 2, 15);
        // Add slight noise
        for (let i = 0; i < 10; i++) {
            ctx.fillStyle = `rgba(${Math.random()*255}, ${Math.random()*255}, ${Math.random()*255}, 0.2)`;
            ctx.fillRect(
                Math.random()*100, 
                Math.random()*100, 
                Math.random()*10, 
                Math.random()*10
            );
        }
        """
        
        return [
            {
                "source": f"""
                // ===== CORE OVERRIDES =====
                // WebGL Spoofing
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(p) {{
                    return p === 37445 ? 'Intel Inc.' : 
                        p === 37446 ? 'Intel Iris OpenGL Engine' :
                        getParameter.call(this, p);
                }};
                
                // Canvas Fingerprint Defense
                HTMLCanvasElement.prototype.toDataURL = function() {{
                    {canvas_script}
                    return this.__realToDataURL();
                }};
                HTMLCanvasElement.prototype.__realToDataURL = HTMLCanvasElement.prototype.toDataURL;
                
                // ===== AUDIO CONTEXT SPOOFING =====
                AudioContext.prototype.createOscillator = function() {{
                    const real = Reflect.apply(...arguments);
                    real.frequency.value = 440 + Math.random()*20;
                    return real;
                }};
                const getFloatFrequencyData = AnalyserNode.prototype.getFloatFrequencyData;
                AnalyserNode.prototype.getFloatFrequencyData = function(array) {{
                    getFloatFrequencyData.call(this, array);
                    for (let i = 0; i < array.length; i++) {{
                        array[i] += (Math.random() * 2) - 1;  // Add noise
                    }}
                }};
                
                // ===== TIMEZONE SPOOFING =====
                Object.defineProperty(Intl, 'DateTimeFormat', {{
                    value: class extends Intl.DateTimeFormat {{
                        constructor(locales, options) {{
                            super(locales, {{...options, timeZone: 'America/New_York'}});
                        }}
                    }}
                }});
                
                // ===== CHROME INTERNALS =====
                Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
                Object.defineProperty(navigator, 'plugins', {{ get: () => [1, 2, 3, 4, 5] }});
                
                // ===== PERFORMANCE TIMING DEFENSE =====
                const performance = window.performance;
                if (performance) {{
                    const realNow = performance.now;
                    performance.now = function() {{
                        return realNow.call(performance) + Math.random() * 10;
                    }};
                }}
                
                // ===== CLEANUP MARKER =====
                delete window.__stealthPatched;
                """
            }
    ] 
    
    # def create_temp_profile(self,chrome_options):
    #     profile_path = tempfile.mkdtemp()
    #     chrome_options.add_argument(f"--user-data-dir={profile_path}")
    #     # Seed with realistic browsing data
    #     os.makedirs(f"{profile_path}/Default/Cache", exist_ok=True)
    #     os.makedirs(f"{profile_path}/Default/Cookies", exist_ok=True)

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
    
    def _get_stealth_scripts(self):
        """Return JavaScript snippets for enhanced stealth"""
        return [
            """
            window.chrome = {
                app: {
                    isInstalled: false,
                },
                webstore: {
                    onInstallStageChanged: {},
                    onDownloadProgress: {},
                },
                runtime: {
                    PlatformOs: {
                        MAC: 'mac',
                        WIN: 'win',
                        ANDROID: 'android',
                        CROS: 'cros',
                        LINUX: 'linux',
                        OPENBSD: 'openbsd',
                    },
                    PlatformArch: {
                        ARM: 'arm',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64',
                    },
                    PlatformNaclArch: {
                        ARM: 'arm',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64',
                    },
                    RequestUpdateCheckStatus: {
                        THROTTLED: 'throttled',
                        NO_UPDATE: 'no_update',
                        UPDATE_AVAILABLE: 'update_available',
                    },
                    OnInstalledReason: {
                        INSTALL: 'install',
                        UPDATE: 'update',
                        CHROME_UPDATE: 'chrome_update',
                        SHARED_MODULE_UPDATE: 'shared_module_update',
                    },
                    OnRestartRequiredReason: {
                        APP_UPDATE: 'app_update',
                        OS_UPDATE: 'os_update',
                        PERIODIC: 'periodic',
                    },
                },
            };
            """
        ]
    def _test_proxy(self, proxy):
        try:
            uc = Browser.get_uc()  # Lazy load happens here
            test_driver = uc.Chrome(options=self._get_test_options(proxy))
            test_driver.get("https://api.ipify.org")
            return True if test_driver.page_source else False
        except:
            return False
    #Post browser launch measures
    def _apply_stealth_measures(self,driver):
        """Apply additional stealth measures from config"""
        stealth(
            driver=driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            **getattr(self, 'proxy_auth', {})  # fallback to empty dict if undefined
  
        )
            # CDP scripts
        for script in self.get_cdp_scripts():
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument", 
                script
            )
        
        # 3. Post-load Chrome API mocking (from _get_stealth_scripts)
        try:
            driver.execute_script(self._get_stealth_scripts()[0])
        except Exception as e:
            print(f"Chrome mock failed: {e}")

        # TODO: FInd Additional scripts that are not included with the selenium stuff and run them if reccommended
        for script in self.get_additional_scripts():
            self.driver.execute_script(script)
        
        # Add mouse entropy if needed
        self.add_mouse_movement_entropy(driver)


    def test_stealth(self, test_url="https://bot.sannysoft.com", delay_seconds = 0):
            """
            Test stealth configuration and keep browser open
            Returns: (driver, results_dict)
            """
            driver = self.create_driver()
            
            try:
                driver.get(test_url)
                driver.implicitly_wait(5)
                if delay_seconds > 0:
                    time.sleep(delay_seconds)  # Wait for specified time
                results = {
                    'user_agent': driver.execute_script("return navigator.userAgent"),
                    'webdriver': driver.execute_script("return navigator.webdriver"),
                    'plugins': driver.execute_script("return navigator.plugins.length"),
                    'timezone': driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone"),
                    'screen_resolution': driver.execute_script("return [window.screen.width, window.screen.height]"),
                    'test_url': test_url
                }
                
                return driver, results
                
            except Exception as e:
                driver.quit()
                raise RuntimeError(f"Stealth test failed: {str(e)}")