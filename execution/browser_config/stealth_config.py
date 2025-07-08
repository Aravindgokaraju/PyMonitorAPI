import os
import tempfile
import random
import shutil
import time
from typing import List, Optional

from execution.browser_config.browser import Browser

class StealthConfig:
    def __init__(self):
        self.max_proxy_retries = 3 
        uc = Browser.get_uc()  # Lazy load happens here
        self.chrome_options = uc.ChromeOptions()
        self.user_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Mac Chrome
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Linux Chrome
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        self.proxies: List[str] = []  # Initialize empty
        self.proxies = [
            "12.34.56.78:8080",
            "user:pass@23.45.67.89:3128",
            "45.67.89.10:8000"
            ]
        self.test_urls = [
            'https://antoinevastel.com/bots/',  # Advanced fingerprinting
            'https://arh.antoinevastel.com/',   # Behavioral analysis
            'https://fingerprint-scan.com/',
            'https://fingerprintjs.com/demo',     # Commercial-grade detection
        ]
        self.profile_path: Optional[str] = None

    def apply(self):
        """Apply all Chrome configuration options"""
        # Core stealth flags
        # self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-infobars")
        
        #Random window size #TODO: make own function
                # Randomize but keep aspect ratio realistic
        self.width = random.choice([1280, 1366, 1440, 1920])
        aspect_ratio = random.uniform(1.6, 1.8)
        self.height = int(self.width / aspect_ratio)
        self.chrome_options.add_argument(
            f"--window-size={self.width},{self.height}"
        )

        # GPU configuration
        self.chrome_options.add_argument("--use-angle=d3d11")  # More widely compatible than vulkan
        self.chrome_options.add_argument("--disable-swiftshader")  # Disable software renderer
        self.chrome_options.add_argument("--ignore-gpu-blocklist")  # Override GPU blocklist
        self.chrome_options.add_argument("--enable-features=DefaultANGLEOpenGL")
        self.chrome_options.add_argument("--enable-gpu-rasterization")
        self.chrome_options.add_argument("--enable-native-gpu-memory-buffers")
        self.chrome_options.add_argument("--enable-oop-rasterization")
        self.chrome_options.add_argument("--enable-features=WebGPU")
        
        #High DPI support
        # self.chrome_options.add_argument("--high-dpi-support=1")
        # self.chrome_options.add_argument("--force-device-scale-factor=1")
        
        # Platform-appropriate user agent

        #TODO: reinstate agent
        # self.chrome_options.add_argument(f"user-agent={random.choice(self.user_agents)}")

        # Proxy configuration (if proxies exist) TODO: re implement proxies
        # if self.proxies:
        #     self._configure_proxy()

        # Profile and rendering settings
        self._create_temp_profile()
        #self.chrome_options.add_argument("--disable-webgl")
        # self.chrome_options.add_argument("--use-gl=desktop")
        self.chrome_options.add_argument("--enable-features=WebGL")
        self.chrome_options.add_argument("--enable-webgl")


        return self.chrome_options



    # def _configure_proxy(self):
    #     """Safe proxy configuration without hardcoded credentials"""
    #     proxy = random.choice(self.proxies)
    #     if "@" in proxy:  # User:pass format
    #         self.chrome_options.add_argument(f'--proxy-server={proxy}')
    #     else:  # IP:PORT format
    #         self.chrome_options.add_argument(f'--proxy-server=http://{proxy}')

    def _configure_proxy(self):
        """Rotate through proxies with validation"""
        uc = Browser.get_uc()  # Lazy load happens here
        if not self.proxies:
            return

        for _ in range(self.max_proxy_retries):
            proxy = random.choice(self.proxies)
            self.current_proxy = proxy
            
            try:
                if "@" in proxy:  # Authenticated proxy
                    self.chrome_options.add_argument(f'--proxy-server={proxy}')
                else:  # IP:PORT format
                    self.chrome_options.add_argument(f'--proxy-server=http://{proxy}')
                    
                # Quick test connection
                test_driver = uc.Chrome(
                    options=self.chrome_options,
                    headless=True,
                    use_subprocess=False,
                    version_main=114
                )
                test_driver.get("http://httpbin.org/ip")
                if test_driver.page_source:
                    test_driver.quit()
                    return  # Success!
                    
            except Exception as e:
                print(f"Proxy failed: {proxy} - {str(e)}")
                self.proxies.remove(proxy)  # Remove bad proxy
                continue
                
        raise RuntimeError("No working proxies available")
    
    def refresh_proxies(self, new_proxies: List[str]):
        """Dynamically update proxy pool"""
        self.proxies = new_proxies
        self.current_proxy = None
    
    def _create_temp_profile(self):
        """Create and manage temporary profile"""
        self.profile_path = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.profile_path, "Default"), exist_ok=True)
        self.chrome_options.add_argument(f"--user-data-dir={self.profile_path}")

    def cleanup(self):
        """Remove temporary profile"""
        if self.profile_path and os.path.exists(self.profile_path):
            shutil.rmtree(self.profile_path)

    def create_driver(self):
        """Safe driver initialization"""
        try:
            uc = Browser.get_uc()  # Lazy load happens here
            self.apply()
            driver = uc.Chrome(
                options=self.chrome_options,
                headless=False,
                use_subprocess=True
                # Let UC detect Chrome version automatically
            )
            self._apply_stealth_measures(driver)
                    # Verify proxy actually works
            driver.get("http://httpbin.org/ip")
            if "origin" not in driver.page_source:
                raise RuntimeError("Proxy verification failed")
                
            return driver
        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to create driver: {str(e)}")

    def _get_realistic_gpu_info(self):
        """Returns realistic GPU information based on platform"""
        gpus = [
            {
                "renderer": "Intel(R) Iris(R) Xe Graphics",
                "vendor": "Intel Inc."
            },
            {
                "renderer": "NVIDIA GeForce RTX 3060",
                "vendor": "NVIDIA Corporation"
            },
            {
                "renderer": "AMD Radeon RX 6700 XT",
                "vendor": "AMD"
            }
        ]
        return random.choice(gpus)

    def _get_realistic_screen_metrics(self):
        """Returns realistic screen metrics"""
        return {
            "width": random.choice([1920, 2560, 3440]),
            "height": random.choice([1080, 1440, 1440]),
            "availWidth": random.choice([1900, 2540, 3400]),
            "availHeight": random.choice([1000, 1400, 1400]),
            "colorDepth": 24,
            "pixelDepth": 24
        }
    
    def _apply_stealth_measures(self, driver):
        """Basic stealth patches with minimal side effects"""
        scripts = [
            # Core patches
            "delete navigator.webdriver;",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4]});",
            
            # Language/device spoofing
            """
            Object.defineProperties(navigator, {
                languages: { get: () => ['en-US', 'en'] },
                deviceMemory: { get: () => 4 },
                hardwareConcurrency: { get: () => 4 }
            });
            """,
            
            # Network spoofing (safe values)
            """
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    rtt: 150,
                    downlink: 3.5,
                    effectiveType: '4g',
                    saveData: false
                })
            });
            """,
          # GPU spoofing WEB GL only - returns realistic WebGL renderer info
          
             """
                // Enhanced WebGL spoofing that creates context if missing
                (function() {
                    const canvas = document.createElement('canvas');
                    try {
                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        
                        if (!gl) {
                            // Force WebGL context creation
                            canvas.getContext = function() {
                                return {
                                    getParameter: function(parameter) {
                                        const debugInfo = {
                                            UNMASKED_RENDERER_WEBGL: 37445,
                                            UNMASKED_VENDOR_WEBGL: 37446
                                        };
                                        if (parameter === debugInfo.UNMASKED_RENDERER_WEBGL) {
                                            return 'Intel(R) Iris(R) Xe Graphics';
                                        }
                                        if (parameter === debugInfo.UNMASKED_VENDOR_WEBGL) {
                                            return 'Intel Inc.';
                                        }
                                        return null;
                                    }
                                };
                            };
                        } else {
                            // Patch existing context
                            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            if (debugInfo) {
                                gl.getParameter = function(parameter) {
                                    if (parameter === debugInfo.UNMASKED_RENDERER_WEBGL) {
                                        return 'Intel(R) Iris(R) Xe Graphics';
                                    }
                                    if (parameter === debugInfo.UNMASKED_VENDOR_WEBGL) {
                                        return 'Intel Inc.';
                                    }
                                    return WebGLRenderingContext.prototype.getParameter.call(this, parameter);
                                };
                            }
                        }
                    } catch(e) {
                        console.error('WebGL spoofing error:', e);
                    }
                })();
            """
            # Spoof GL_RENDERER globally
            """
                (function spoofGlRenderer() {
                    const origGetParam = WebGLRenderingContext.prototype.getParameter;
                    
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        // Try to get the constants from the context, fall back to known values
                        const RENDERER = this.RENDERER || 0x1F01;
                        const VENDOR = this.VENDOR || 0x1F00;
                        
                        if (parameter === RENDERER) {
                            return 'Intel(R) Iris(R) Xe Graphics';
                        }
                        if (parameter === VENDOR) {
                            return 'Intel Inc.';
                        }
                        return origGetParam.call(this, parameter);
                    };
                })();
            """,
                        
            """
                if ('gpu' in navigator) {
                    Object.defineProperty(navigator, 'gpu', {
                        value: {
                            requestAdapter: () => Promise.resolve({
                                name: 'Intel(R) Iris(R) Xe Graphics',
                                vendor: 'Intel',
                                adapterType: 'integrated',
                                deviceType: 'GPU'
                            })
                        },
                        configurable: false
                    });
                }
            """,
            """
                if ('gpu' in navigator) {
                    console.log('WebGPU available');
                } else {
                    console.warn('WebGPU NOT available');
                }
            """,
            
            # Screen metrics spoofing (keep this consistent with window size)
            f"""
            Object.defineProperties(window.screen, {{
                width: {{ get: () => {self.width} }},
                height: {{ get: () => {self.height} }},
                availWidth: {{ get: () => {random.randint(1900, 2500)} }},
                availHeight: {{ get: () => {random.randint(1000, 1400)} }},
                colorDepth: {{ get: () => 24 }},
                pixelDepth: {{ get: () => 24 }}
            }});
            """,
            
            # Device pixel ratio spoofing
            """
            Object.defineProperty(window, 'devicePixelRatio', {
                get: () => 1,
                configurable: true
            });
            """,
            
            # WebDriver flag removal (more thorough)
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true,
                enumerable: true
            });
            delete window._selenium;
            delete window.callPhantom;
            delete window.phantom;
            delete window.__nightmare;
            delete window._WEBDRIVER_ELEM_CACHE;
            """
        ]
        
        for script in scripts:
            try:
                driver.execute_script(script)
            except:
                pass  # Fail silently to avoid breaking the driver


    def cleanup(self):
        """Remove temporary profile with retries and error handling"""
        if not self.profile_path or not os.path.exists(self.profile_path):
            return

        max_retries = 3
        retry_delay = 0.5  # seconds between retries
        
        for attempt in range(max_retries):
            try:
                shutil.rmtree(self.profile_path)
                break  # Success!
            except (PermissionError, OSError) as e:
                if attempt == max_retries - 1:  # Final attempt failed
                    print(f"⚠️ Failed to cleanup profile after {max_retries} attempts: {str(e)}")
                    print(f"Profile directory retained at: {self.profile_path}")
                time.sleep(retry_delay)

    def test_stealth(self, test_url="https://bot.sannysoft.com/", delay_seconds=0):
        """
        Test stealth configuration with proper resource cleanup
        Returns: (driver, results_dict)
        """
        test_url = self.test_urls[2]
        driver = None
        try:
            driver = self.create_driver()
            driver.get(test_url)
            driver.implicitly_wait(5)
            
            if delay_seconds > 0:
                time.sleep(delay_seconds)
                
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
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"⚠️ Error while quitting driver: {str(quit_error)}")
            self.cleanup()
            raise RuntimeError(f"Stealth test failed: {str(e)}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"⚠️ Error in final driver cleanup: {str(quit_error)}")
            self.cleanup()