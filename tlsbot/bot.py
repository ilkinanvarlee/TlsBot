
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import asyncio
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv
import os

load_dotenv()




import random
import tempfile
import uuid
import subprocess








class TLSBot:
    
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    LOGIN_URL = os.getenv("LOGIN_URL")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    NO_SLOT_CHANNEL_ID = os.getenv("NO_SLOT_CHANNEL_ID")
    CALENDAR_CHANNEL_ID = os.getenv("CALENDAR_CHANNEL_ID")
    
    # Multiple proxy endpoints from your Webshare account
    PROXY_LIST = [
        {
            'host': '198.23.239.134',  # United States - Buffalo (Current)
            'port': '6540',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '207.244.217.165',  # Croatia - Zagreb
            'port': '6712',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '107.172.163.27',  # United States - Bloomingdale
            'port': '6543',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '23.94.138.75',  # United States - Buffalo
            'port': '6349',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '216.10.27.159',  # United States - Dallas
            'port': '6837',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '136.0.207.84',  # United States - Orem
            'port': '6661',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '64.64.118.149',  # United States - Greenlawn
            'port': '6732',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '142.147.128.93',  # United States - Ashburn
            'port': '6593',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '104.239.105.125',  # United States - Dallas
            'port': '6655',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        },
        {
            'host': '173.0.9.70',  # United States - Ashburn
            'port': '5653',
            'user': 'dfbhwtck',
            'pass': '16lu6q7n6w2m'
        }
    ]

    def __init__(self):
        self.cleanup_chrome_processes()
        time.sleep(2)
        self.current_proxy_index = 0
        self.max_retries = len(self.PROXY_LIST)
        self.driver = None
        self.wait = None
        self.current_proxy = None
        self.setup_driver_with_rotation()

    def cleanup_chrome_processes(self):
        """Kill any existing Chrome processes"""
        try:
            subprocess.run(["pkill", "-f", "chrome"], check=False)
            subprocess.run(["pkill", "-f", "chromium"], check=False)
            subprocess.run(["pkill", "-f", "chromedriver"], check=False)
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def login_with_proxy_switch(self):
        """Login with immediate proxy switch after form submission"""
        self.driver.get(self.LOGIN_URL)
        time.sleep(5)

        try:
            if self.is_blocked():
                print("🚫 Blocked on login page")
                return False

            print(f"Initial page title: {self.driver.title}")
            print(f"Initial URL: {self.driver.current_url}")
            
            # Find and fill login form (keep existing logic)
            email_field = None
            try:
                email_field = self.wait.until(EC.visibility_of_element_located((By.ID, "email-input-field")))
            except:
                try:
                    email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
                except:
                    try:
                        email_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
                    except:
                        print("❌ Email field not found")
                        return False
            
            if email_field:
                email_field.send_keys(self.EMAIL)
                time.sleep(2)
                
                # Find password field
                password_field = None
                try:
                    password_field = self.wait.until(EC.visibility_of_element_located((By.ID, "password-input-field")))
                except:
                    try:
                        password_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "password")))
                    except:
                        try:
                            password_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
                        except:
                            print("❌ Password field not found")
                            return False
                
                if password_field:
                    password_field.send_keys(self.PASSWORD)
                    time.sleep(2)
                    
                    # Find login button
                    login_button = None
                    try:
                        login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "btn-login")))
                    except:
                        try:
                            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                        except:
                            try:
                                login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']")))
                            except:
                                print("❌ Login button not found")
                                return False
                    
                    if login_button:
                        print("🔄 About to click login - preparing for proxy switch...")
                        
                        # STRATEGY 1: Extract cookies and session data before clicking
                        cookies_before = self.driver.get_cookies()
                        session_storage = self.driver.execute_script("return window.sessionStorage;")
                        local_storage = self.driver.execute_script("return window.localStorage;") 
                        
                        print(f"📦 Saved {len(cookies_before)} cookies before login")
                        
                        # Click login button
                        login_button.click()
                        print("🔄 Login clicked - waiting briefly...")
                        
                        # Wait very short time for form submission
                        time.sleep(2)
                        
                        # IMMEDIATELY switch to new proxy before redirect completes
                        print("🔄 Switching proxy mid-session...")
                        return self.continue_with_new_proxy(cookies_before, session_storage, local_storage)
            
            return False
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def continue_with_new_proxy(self, cookies_before, session_storage, local_storage):
        """Continue session with new proxy and preserved session data"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']}")
            
            # Quit current driver
            current_url = self.driver.current_url
            self.driver.quit()
            time.sleep(1)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to the auth-callback URL or dashboard directly
            print("🔄 Navigating with new proxy...")
            
            # Try different continuation strategies
            success = False
            
            # Strategy 1: Try to go directly to dashboard/travel groups
            dashboard_urls = [
                "https://visas-de.tlscontact.com/en-us/travel-groups",
                "https://visas-de.tlscontact.com/en-us/dashboard",
                "https://visas-de.tlscontact.com/en-us/"
            ]
            
            for url in dashboard_urls:
                try:
                    print(f"🔗 Trying direct access to: {url}")
                    self.driver.get(url)
                    self.driver.save_screenshot("/tmp/select_page_new_proxy3.png")
                    time.sleep(5)
                    
                    # Restore cookies and session
                    for cookie in cookies_before:
                        try:
                            self.driver.add_cookie(cookie)
                        except:
                            pass
                    
                    # Refresh after adding cookies
                    self.driver.refresh()
                    time.sleep(5)
                    
                    # Check if we're successfully logged in
                    current_url = self.driver.current_url
                    self.driver.save_screenshot("/tmp/select_page_new_proxy4.png")
                    page_source = self.driver.page_source.lower()
                    
                    print(f"📍 After cookie restore: {current_url}")
                    
                    # Check for success indicators
                    if ("travel" in current_url.lower() or 
                        "dashboard" in current_url.lower() or
                        "select" in page_source or
                        "appointment" in page_source):
                        self.driver.save_screenshot("/tmp/select_page_new_proxy5.png")
                        print("✅ Successfully accessed with new proxy!")

                        success = True
                        break
                        
                    elif self.is_blocked():
                        print(f"🚫 Still blocked with {new_proxy['host']}")
                        continue
                    else:
                        print(f"🤔 Uncertain status with {url}")
                        
                except Exception as e:
                    print(f"⚠️ Error trying {url}: {e}")
                    continue
            
            # Strategy 2: If direct access failed, try the original auth flow
            if not success:
                print("🔄 Direct access failed, trying fresh login with new proxy...")
                return self.login()  # Regular login with new proxy
            
            return success
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False

    def run_with_mid_session_switching(self):
        """Enhanced run method with mid-session proxy switching"""
        max_attempts = len(self.PROXY_LIST) * 3  # More attempts since we switch mid-session
        
        for attempt in range(max_attempts):
            try:
                print(f"🚀 Enhanced bot run attempt {attempt + 1}")
                
                # Use the new login method with proxy switching
                if self.login_with_proxy_switch():
                    if self.click_first_select():
                        if self.click_continue():
                            self.wait_final_page()
                            return True  # Success!
                            
                # If failed, try next proxy
                print("🔄 Attempt failed, rotating to next proxy...")
                self.rotate_proxy_if_blocked()
                continue
                        
            except Exception as e:
                print(f"⚠️ Enhanced bot run error: {e}")
                self.rotate_proxy_if_blocked()
                continue
        
        print("❌ All enhanced attempts failed")
        return False

    def get_next_proxy(self):
        """Get the next proxy in rotation"""
        if not self.PROXY_LIST:
            return None
        proxy = self.PROXY_LIST[self.current_proxy_index % len(self.PROXY_LIST)]
        self.current_proxy_index += 1
        return proxy

    def test_proxy(self, proxy):
        """Test if a proxy is working"""
        try:
            print(f"🧪 Testing proxy {proxy['host']}:{proxy['port']}")
            proxy_url = f"http://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}"
            proxies = {'http': proxy_url, 'https': proxy_url}
            
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Proxy working - IP: {result.get('origin', 'unknown')}")
                return True
            else:
                print(f"❌ Proxy test failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Proxy test error: {e}")
            return False

    def setup_driver_with_rotation(self):
        """Setup driver with proxy rotation"""
        for attempt in range(self.max_retries):
            try:
                proxy = self.get_next_proxy()
                if not proxy:
                    print("❌ No proxies available")
                    break
                
                print(f"🔄 Attempt {attempt + 1}/{self.max_retries} - Trying proxy {proxy['host']}")
                
                # Test proxy first
                if not self.test_proxy(proxy):
                    print(f"⚠️ Proxy {proxy['host']} failed test, trying next...")
                    continue
                
                # Setup driver with this proxy
                self.driver = self.create_driver_with_proxy(proxy)
                if self.driver:
                    self.wait = WebDriverWait(self.driver, 20)
                    self.current_proxy = proxy
                    
                    # Test driver with a simple request
                    if self.test_driver():
                        print(f"✅ Successfully setup driver with proxy {proxy['host']}")
                        return True
                    else:
                        print(f"❌ Driver test failed with proxy {proxy['host']}")
                        if self.driver:
                            self.driver.quit()
                        continue
            except Exception as e:
                print(f"❌ Error setting up driver: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                continue
        
        print("❌ Failed to setup driver with any proxy")
        raise Exception("All proxies failed")

    def create_driver_with_proxy(self, proxy):
        """Create Chrome driver with specific proxy"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Randomize window size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            chrome_options.add_argument(f"--window-size={width},{height}")
            
            # User data directory
            temp_dir = tempfile.mkdtemp()
            chrome_options.add_argument(f"--user-data-dir={temp_dir}/{uuid.uuid4()}")
            chrome_options.add_argument("--remote-debugging-port=0")
            
            # Create proxy extension
            extension_dir = self.create_proxy_extension(proxy, temp_dir)
            if extension_dir:
                chrome_options.add_argument(f"--load-extension={extension_dir}")
                print(f"🔧 Created proxy auth extension")
            
            # Anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ]
            chosen_ua = random.choice(user_agents)
            chrome_options.add_argument(f"--user-agent={chosen_ua}")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Execute stealth scripts
            stealth_scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                "window.chrome = { runtime: {} }"
            ]
            
            for script in stealth_scripts:
                try:
                    driver.execute_script(script)
                except:
                    pass
            
            time.sleep(3)  # Wait for extension to load
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create driver: {e}")
            return None

    def create_proxy_extension(self, proxy, temp_dir):
        """Create proxy authentication extension"""
        try:
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Proxy Auth",
                "permissions": [
                    "proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>",
                    "webRequest", "webRequestBlocking"
                ],
                "background": {"scripts": ["background.js"]},
                "minimum_chrome_version":"22.0.0"
            }
            """
            
            background_js = f"""
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{proxy['host']}",
                        port: parseInt({proxy['port']})
                    }},
                    bypassList: ["localhost"]
                }}
            }};

            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            chrome.webRequest.onAuthRequired.addListener(
                function(details) {{
                    return {{
                        authCredentials: {{
                            username: "{proxy['user']}",
                            password: "{proxy['pass']}"
                        }}
                    }};
                }},
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """
            
            extension_dir = f"{temp_dir}/proxy_extension_{random.randint(1000, 9999)}"
            os.makedirs(extension_dir, exist_ok=True)
            
            with open(f"{extension_dir}/manifest.json", "w") as f:
                f.write(manifest_json)
            
            with open(f"{extension_dir}/background.js", "w") as f:
                f.write(background_js)
            
            return extension_dir
        except Exception as e:
            print(f"❌ Failed to create proxy extension: {e}")
            return None

    def test_driver(self):
        """Test if driver is working properly"""
        try:
            self.driver.get("https://httpbin.org/ip")
            time.sleep(3)
            if "httpbin" in self.driver.title.lower() or "origin" in self.driver.page_source:
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Driver test error: {e}")
            return False

    def rotate_proxy_if_blocked(self):
        """Rotate to next proxy if current one is blocked"""
        print("🔄 Rotating proxy due to blocking...")
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        # Try next proxy
        self.setup_driver_with_rotation()

    def is_blocked(self):
        """Check if current page shows blocking"""
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            blocking_indicators = [
                "error 1005",
                "access denied",
                "banned",
                "cloudflare",
                "ray id:",
                "please enable cookies"
            ]
            
            return any(indicator in page_source for indicator in blocking_indicators)
        except:
            return False

   

    
    def click_continue(self):
        try:
            self.wait.until(EC.url_contains("/workflow/service-level"))
            continue_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')]")))
            self.driver.execute_script("arguments[0].click();", continue_btn)
            print("✅ 'Continue' düyməsi klikləndi (JS click)!")
            return True
        except Exception as e:
            print(f"❌ 'Continue' kliklənmədi: {e}")
            return False

    def print_appointment_info(self):
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            start_text = "We currently don't have any appointment slots available."
            end_text = "as it is frequently updated with newly available slots."

            if start_text in body_text and end_text in body_text:
                start_index = body_text.find(start_text)
                end_index = body_text.find(end_text) + len(end_text)
                full_message = body_text[start_index:end_index]

                warning_message = (
                    "⚠️ Hazırda heç bir təyin edilmiş vaxt yoxdur.\n"
                    "Mesaj:\n" + full_message
                )
                self.send_telegram_message(self.NO_SLOT_CHANNEL_ID, warning_message)
            else:
                try:
                    calendar_elem = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "appointment-calendar"))
                    )
                    calendar_text = calendar_elem.text
                    self.send_telegram_message(self.CALENDAR_CHANNEL_ID, f"📅 Yeni vaxt mövcuddur:\n\n{calendar_text}")
                except TimeoutException:
                    print("⚠️ Təqvim görünməli idi, amma tapılmadı.")
                    self.send_telegram_message(self.CALENDAR_CHANNEL_ID, "📅 Yeni slot mövcuddur, amma təqvim tapılmadı (class adı dəyişmiş ola bilər).")
        
        except Exception as e:
            print(f"❌ Məlumatlar götürülərkən xəta baş verdi: {e}")

    def wait_final_page(self):
        try:
            self.wait.until(EC.url_contains("appointment-booking"))
            print("🔗 Son URL:", self.driver.current_url)
            time.sleep(2)
            self.print_appointment_info()
        except Exception as e:
            print(f"❌ Son səhifəyə keçid alınmadı: {e}")

    def run_with_rotation(self):
        """Run the bot with proxy rotation on failures"""
        max_rotation_attempts = len(self.PROXY_LIST) * 2
        
        for rotation_attempt in range(max_rotation_attempts):
            try:
                print(f"🚀 Bot run attempt {rotation_attempt + 1}")
                
                if self.login():
                    if self.click_first_select():
                        if self.click_continue():
                            self.wait_final_page()
                            return True  # Success!
                        
                # Check if it's a blocking issue
                if self.is_blocked():
                    print("🚫 Detected blocking, rotating proxy...")
                    self.rotate_proxy_if_blocked()
                    continue
                else:
                    print("❌ Failed for other reasons")
                    break
                    
            except Exception as e:
                print(f"⚠️ Bot run error: {e}")
                if self.is_blocked() or "proxy" in str(e).lower() or "connection" in str(e).lower():
                    print("🔄 Connection issue, rotating proxy...")
                    self.rotate_proxy_if_blocked()
                    continue
                else:
                    break
        
        print("❌ All rotation attempts failed")
        return False
    
    

    def run(self):
        """Main run method - now uses immediate switching"""
        return self.run_with_immediate_switching()

    def send_telegram_message(self, chat_id, message):
        url = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"📤 Telegram mesajı göndərildi: {chat_id}")
            else:
                print(f"❌ Telegram xətası: {response.text}")
        except Exception as e:
            print(f"❌ Telegram bildirişi xətası: {e}")


    def switch_proxy_and_navigate_to_select(self, cookies_before):
        """Switch proxy immediately and navigate to Select page"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']} for SELECT step")
            
            # Quit current driver
            self.driver.quit()
            time.sleep(2)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to travel-groups page
            target_url = "https://visas-de.tlscontact.com/en-us/travel-groups"
            print(f"🔗 Navigating with new proxy to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're successfully on the page
            current_url = self.driver.current_url
            print(f"📍 After cookie restore: {current_url}")
            
            if self.is_blocked():
                print("🚫 Still blocked after proxy switch")
                return False
            
            print("✅ Successfully navigated with new proxy!")
            return True
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False

    def click_select_and_immediate_switch(self):
        """Click Select button and immediately switch proxy"""
        try:
            # Wait for page to load
            time.sleep(5)
            
            print(f"🎯 Looking for Select button...")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check if blocked
            if self.is_blocked():
                print("🚫 Blocked on select page")
                return False
            
            # Find Select buttons
            buttons = []
            try:
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')] | //a[contains(text(), 'Select')] | //input[@value='Select']")
                if buttons:
                    print(f"✅ Found {len(buttons)} Select button(s)")
                else:
                    print("❌ No Select buttons found")
                    return False
            except Exception as e:
                print(f"⚠️ Error finding Select buttons: {e}")
                return False
            
            if buttons:
                # Save cookies before clicking
                cookies_before = self.driver.get_cookies()
                print(f"📦 Saved {len(cookies_before)} cookies before SELECT")
                
                # Click the first Select button
                try:
                    self.driver.execute_script("arguments[0].click();", buttons[0])
                    time.sleep(3)
                    print("✅ Select button clicked!")
                    
                    # Check if we were redirected successfully
                    current_url = self.driver.current_url
                    if "/workflow/service-level" in current_url:
                        print(f"✅ Select successful - reached: {current_url}")
                        
                        # IMMEDIATELY switch proxy for CONTINUE step
                        print("🚀 Select successful! Immediately switching proxy for CONTINUE step...")
                        return self.switch_proxy_and_navigate_to_continue(cookies_before)
                    else:
                        print(f"⚠️ Unexpected URL after Select: {current_url}")
                        return False
                        
                except Exception as e:
                    print(f"⚠️ Select click error: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Select step error: {e}")
            return False

    def switch_proxy_and_navigate_to_continue(self, cookies_before):
        """Switch proxy immediately and navigate to Continue page"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']} for CONTINUE step")
            
            # Quit current driver
            self.driver.quit()
            time.sleep(2)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to service-level page
            target_url = "https://visas-de.tlscontact.com/en-us/workflow/service-level"
            print(f"🔗 Navigating with new proxy to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're successfully on the page
            current_url = self.driver.current_url
            print(f"📍 After cookie restore: {current_url}")
            
            if self.is_blocked():
                print("🚫 Still blocked after proxy switch")
                return False
            
            print("✅ Successfully navigated to Continue page with new proxy!")
            return True
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False

    def click_continue_and_immediate_switch(self):
        """Click Continue button and immediately switch proxy"""
        try:
            # Wait for page to load
            time.sleep(5)
            
            print(f"➡️ Looking for Continue button...")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if blocked
            if self.is_blocked():
                print("🚫 Blocked on continue page")
                return False
            
            # Find Continue button
            try:
                continue_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')] | //button[contains(text(),'Continue')]")))
                
                # Save cookies before clicking
                cookies_before = self.driver.get_cookies()
                print(f"📦 Saved {len(cookies_before)} cookies before CONTINUE")
                
                # Click Continue button
                self.driver.execute_script("arguments[0].click();", continue_btn)
                time.sleep(3)
                print("✅ Continue button clicked!")
                
                # Check if we were redirected successfully
                current_url = self.driver.current_url
                if "appointment-booking" in current_url:
                    print(f"✅ Continue successful - reached: {current_url}")
                    
                    # IMMEDIATELY switch proxy for FINAL step
                    print("🚀 Continue successful! Immediately switching proxy for FINAL step...")
                    return self.switch_proxy_and_navigate_to_final(cookies_before)
                else:
                    print(f"⚠️ Unexpected URL after Continue: {current_url}")
                    return False
                    
            except Exception as e:
                print(f"❌ Continue button error: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Continue step error: {e}")
            return False

    def switch_proxy_and_navigate_to_final(self, cookies_before):
        """Switch proxy immediately and navigate to final page"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']} for FINAL step")
            
            # Quit current driver
            self.driver.quit()
            time.sleep(2)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to appointment-booking page
            target_url = "https://visas-de.tlscontact.com/en-us/appointment-booking"
            print(f"🔗 Navigating with new proxy to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're successfully on the page
            current_url = self.driver.current_url
            print(f"📍 After cookie restore: {current_url}")
            
            if self.is_blocked():
                print("🚫 Still blocked after proxy switch")
                return False
            
            print("✅ Successfully navigated to final page with new proxy!")
            return True
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False
        
    def switch_proxy_then_click_select(self):
        """Switch proxy FIRST, then look for and click Select button"""
        try:
            print("🔄 STEP 1: Switching proxy BEFORE Select step...")
            
            # Save current session data
            cookies_before = self.driver.get_cookies() if self.driver else []
            current_url = self.driver.current_url if self.driver else ""
            
            print(f"📦 Saving {len(cookies_before)} cookies before proxy switch")
            print(f"📍 Current URL: {current_url}")
            
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔧 Switching to proxy: {new_proxy['host']} BEFORE Select step")
            self.driver.save_screenshot("/tmp/select_page_new_proxy1.png")
            # Quit current driver
            if self.driver:
                self.driver.quit()
            
            time.sleep(2)
            
            # Create new driver with fresh proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            print("🔄 STEP 2: Navigating to Select page with new proxy...")
            
            # Navigate to travel-groups page
            target_url = "https://visas-de.tlscontact.com/en-us/travel-groups"
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if page loaded successfully
            current_url = self.driver.current_url
            print(f"📍 After proxy switch and navigation: {current_url}")
            
            if self.is_blocked():
                print(f"🚫 Blocked with new proxy {new_proxy['host']}")
                return False
            
            print("✅ Successfully switched proxy and navigated to Select page!")
            
            print("🔄 STEP 3: Looking for Select button with new proxy...")
            
            # Now look for Select button with fresh IP
            return self.find_and_click_select_button()
            
        except Exception as e:
            print(f"❌ Proxy switch before Select error: {e}")
            return False

    def find_and_click_select_button(self):
        """Find and click Select button (called after proxy switch)"""
        try:
            # Wait for page to load
            time.sleep(5)
            
            print(f"🎯 Looking for Select button...")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check if blocked
            if self.is_blocked():
                print("🚫 Blocked on select page")
                return False
            
            # Try different ways to find the select button
            buttons = []
            
            try:
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')]")
                if buttons:
                    print(f"✅ Found {len(buttons)} 'Select' buttons")
                else:
                    # Try other variations
                    buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'select')] | //input[@value='Select'] | //a[contains(text(), 'Select')]")
                    if buttons:
                        print(f"✅ Found {len(buttons)} Select elements")
            except Exception as e:
                print(f"⚠️ Error finding Select buttons: {e}")
            
            # Debug: Print all clickable elements if no Select button found
            if not buttons:
                print("🔍 All clickable elements on page:")
                try:
                    all_buttons = self.driver.find_elements(By.XPATH, "//button | //input[@type='submit'] | //input[@type='button'] | //a[contains(@class, 'btn')]")
                    for i, btn in enumerate(all_buttons[:10]):
                        try:
                            text = btn.text.strip()
                            tag = btn.tag_name
                            classes = btn.get_attribute('class')
                            print(f"  {i+1}. <{tag}> '{text}' (class: {classes})")
                        except:
                            pass
                except Exception as e:
                    print(f"⚠️ Error getting clickable elements: {e}")
                
                try:
                    self.driver.save_screenshot("/tmp/select_page_new_proxy.png")
                    print("📸 Screenshot saved: /tmp/select_page_new_proxy.png")
                except:
                    pass
                
                print("❌ 'Select' düyməsi tapılmadı.")
                return False
            
            # If we found buttons, click the first one
            if buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", buttons[0])
                    time.sleep(3)
                    print("✅ 'Select' düyməsi klikləndi (JS click)!")
                    
                    # Check if we were redirected successfully
                    current_url = self.driver.current_url
                    print(f"📍 After Select click: {current_url}")
                    
                    if "/workflow/service-level" in current_url or "workflow" in current_url:
                        print("✅ Select successful - redirected to workflow page!")
                        return True
                    else:
                        print(f"🤔 Select clicked but unexpected URL: {current_url}")
                        return True  # Still consider it success if no blocking
                        
                except Exception as e:
                    print(f"⚠️ Select klik xətası: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Find and click Select error: {e}")
            return False
    def run_with_immediate_switching(self):
        """Main run method with immediate proxy switching after each successful step"""
        max_attempts = len(self.PROXY_LIST)
        
        for attempt in range(max_attempts):
            try:
                print(f"🚀 Immediate switching run attempt {attempt + 1}")
                
                # STEP 1: Login and immediate switch
                if self.login_and_immediate_switch():
                    self.driver.save_screenshot("/tmp/select_page_new_proxy2.png")
                    print("✅ Login and proxy switch successful!")
                    
                    # STEP 2: Select and immediate switch
                    if self.switch_proxy_then_click_select():
                        print("✅ Select and proxy switch successful!")
                        
                        # STEP 3: Continue and immediate switch
                        if self.click_continue_and_immediate_switch():
                            print("✅ Continue and proxy switch successful!")
                            
                            # STEP 4: Final page processing
                            try:
                                self.print_appointment_info()
                                print("🎉 SUCCESS! Completed all steps with immediate switching!")
                                return True
                            except Exception as e:
                                print(f"⚠️ Final step error: {e}")
                        else:
                            print("❌ Continue step failed")
                    else:
                        print("❌ Select step failed")
                else:
                    print("❌ Login step failed")
                
                # If any step failed, try with next proxy
                print("🔄 Attempt failed, trying with next proxy...")
                
            except Exception as e:
                print(f"⚠️ Run attempt error: {e}")
                continue
        
        print("❌ All immediate switching attempts failed")
        return False

            
    def login_and_immediate_switch(self):
    
        """Login with immediate proxy switch after form submission"""
        self.driver.get(self.LOGIN_URL)
        time.sleep(5)

        try:
            if self.is_blocked():
                print("🚫 Blocked on login page")
                return False

            print(f"Initial page title: {self.driver.title}")
            print(f"Initial URL: {self.driver.current_url}")
            
            # Find and fill login form (keep existing logic)
            email_field = None
            try:
                email_field = self.wait.until(EC.visibility_of_element_located((By.ID, "email-input-field")))
            except:
                try:
                    email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
                except:
                    try:
                        email_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']")))
                    except:
                        print("❌ Email field not found")
                        return False
            
            if email_field:
                email_field.send_keys(self.EMAIL)
                time.sleep(2)
                
                # Find password field
                password_field = None
                try:
                    password_field = self.wait.until(EC.visibility_of_element_located((By.ID, "password-input-field")))
                except:
                    try:
                        password_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "password")))
                    except:
                        try:
                            password_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
                        except:
                            print("❌ Password field not found")
                            return False
                
                if password_field:
                    password_field.send_keys(self.PASSWORD)
                    time.sleep(2)
                    
                    # Find login button
                    login_button = None
                    try:
                        login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "btn-login")))
                    except:
                        try:
                            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                        except:
                            try:
                                login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']")))
                            except:
                                print("❌ Login button not found")
                                return False
                    
                    if login_button:
                        print("🔄 About to click login - preparing for proxy switch...")
                        
                        # STRATEGY 1: Extract cookies and session data before clicking
                        cookies_before = self.driver.get_cookies()
                        session_storage = self.driver.execute_script("return window.sessionStorage;")
                        local_storage = self.driver.execute_script("return window.localStorage;") 
                        
                        print(f"📦 Saved {len(cookies_before)} cookies before login")
                        
                        # Click login button
                        login_button.click()
                        print("🔄 Login clicked - waiting briefly...")
                        
                        # Wait very short time for form submission
                        time.sleep(2)
                        
                        # IMMEDIATELY switch to new proxy before redirect completes
                        print("🔄 Switching proxy mid-session...")
                        return self.continue_with_new_proxy(cookies_before, session_storage, local_storage)
            
            return False
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def switch_proxy_mid_auth_flow(self, cookies_before):
        """Switch proxy immediately during auth flow"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Mid-auth switching to proxy: {new_proxy['host']}")
            
            # Quit current driver immediately
            self.driver.quit()
            time.sleep(1)  # Minimal wait
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Try multiple strategies to continue the auth flow
            success = False
            
            # Strategy 1: Try direct travel-groups access
            dashboard_urls = [
                "https://visas-de.tlscontact.com/en-us/travel-groups",
                "https://visas-de.tlscontact.com/en-us/dashboard",
                "https://visas-de.tlscontact.com/en-us/"
            ]
            
            for url in dashboard_urls:
                try:
                    print(f"🔗 Trying direct access to: {url}")
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # Restore cookies from before login
                    for cookie in cookies_before:
                        try:
                            self.driver.add_cookie(cookie)
                        except:
                            pass
                    
                    # Refresh to apply cookies
                    self.driver.refresh()
                    time.sleep(5)
                    
                    current_url = self.driver.current_url
                    page_source = self.driver.page_source.lower()
                    
                    print(f"📍 After cookie restore: {current_url}")
                    
                    # Check for success indicators
                    if self.is_blocked():
                        print(f"🚫 Still blocked with {new_proxy['host']} at {url}")
                        continue
                    elif ("travel" in current_url.lower() or 
                        "dashboard" in current_url.lower() or
                        "select" in page_source):
                        print("✅ Successfully accessed with new proxy!")
                        success = True
                        break
                    else:
                        print(f"🤔 Uncertain status with {url}")
                        # Try next URL
                        
                except Exception as e:
                    print(f"⚠️ Error trying {url}: {e}")
                    continue
            
            # Strategy 2: If direct access failed, try fresh auth flow
            if not success:
                print("🔄 Direct access failed, trying fresh login with new proxy...")
                
                # Try a fresh login with the new proxy
                self.driver.get(self.LOGIN_URL)
                time.sleep(5)
                
                if not self.is_blocked():
                    print("✅ Fresh login page accessible with new proxy")
                    return True  # Return True to continue with SELECT step
                else:
                    print("🚫 Fresh login also blocked")
                    return False
            
            return success
            
        except Exception as e:
            print(f"❌ Mid-auth proxy switch error: {e}")
            return False



    def click_select_and_immediate_switch(self):
        """Click Select button and immediately switch proxy"""
        try:
            # Wait for page to load
            time.sleep(5)
            
            print(f"🎯 Looking for Select button...")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check if blocked
            if self.is_blocked():
                print("🚫 Blocked on select page")
                return False
            
            # Find Select buttons
            buttons = []
            try:
                buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')] | //a[contains(text(), 'Select')] | //input[@value='Select']")
                if buttons:
                    print(f"✅ Found {len(buttons)} Select button(s)")
                else:
                    print("❌ No Select buttons found")
                    return False
            except Exception as e:
                print(f"⚠️ Error finding Select buttons: {e}")
                return False
            
            if buttons:
                # Save cookies before clicking
                cookies_before = self.driver.get_cookies()
                print(f"📦 Saved {len(cookies_before)} cookies before SELECT")
                
                # Click the first Select button
                try:
                    self.driver.execute_script("arguments[0].click();", buttons[0])
                    time.sleep(3)
                    print("✅ Select button clicked!")
                    
                    # Check if we were redirected successfully
                    current_url = self.driver.current_url
                    if "/workflow/service-level" in current_url:
                        print(f"✅ Select successful - reached: {current_url}")
                        
                        # IMMEDIATELY switch proxy for CONTINUE step
                        print("🚀 Select successful! Immediately switching proxy for CONTINUE step...")
                        return self.switch_proxy_and_navigate_to_continue(cookies_before)
                    else:
                        print(f"⚠️ Unexpected URL after Select: {current_url}")
                        return False
                        
                except Exception as e:
                    print(f"⚠️ Select click error: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Select step error: {e}")
            return False

    def switch_proxy_and_navigate_to_continue(self, cookies_before):
        """Switch proxy immediately and navigate to Continue page"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']} for CONTINUE step")
            
            # Quit current driver
            self.driver.quit()
            time.sleep(2)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to service-level page
            target_url = "https://visas-de.tlscontact.com/en-us/workflow/service-level"
            print(f"🔗 Navigating with new proxy to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're successfully on the page
            current_url = self.driver.current_url
            print(f"📍 After cookie restore: {current_url}")
            
            if self.is_blocked():
                print("🚫 Still blocked after proxy switch")
                return False
            
            print("✅ Successfully navigated to Continue page with new proxy!")
            return True
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False

    def click_continue_and_immediate_switch(self):
        """Click Continue button and immediately switch proxy"""
        try:
            # Wait for page to load
            time.sleep(5)
            
            print(f"➡️ Looking for Continue button...")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if blocked
            if self.is_blocked():
                print("🚫 Blocked on continue page")
                return False
            
            # Find Continue button
            try:
                continue_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Continue')] | //button[contains(text(),'Continue')]")))
                
                # Save cookies before clicking
                cookies_before = self.driver.get_cookies()
                print(f"📦 Saved {len(cookies_before)} cookies before CONTINUE")
                
                # Click Continue button
                self.driver.execute_script("arguments[0].click();", continue_btn)
                time.sleep(3)
                print("✅ Continue button clicked!")
                
                # Check if we were redirected successfully
                current_url = self.driver.current_url
                if "appointment-booking" in current_url:
                    print(f"✅ Continue successful - reached: {current_url}")
                    
                    # IMMEDIATELY switch proxy for FINAL step
                    print("🚀 Continue successful! Immediately switching proxy for FINAL step...")
                    return self.switch_proxy_and_navigate_to_final(cookies_before)
                else:
                    print(f"⚠️ Unexpected URL after Continue: {current_url}")
                    return False
                    
            except Exception as e:
                print(f"❌ Continue button error: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Continue step error: {e}")
            return False

    def switch_proxy_and_navigate_to_final(self, cookies_before):
        """Switch proxy immediately and navigate to final page"""
        try:
            # Get next proxy
            new_proxy = self.get_next_proxy()
            if not new_proxy:
                print("❌ No more proxies available")
                return False
            
            print(f"🔄 Switching to proxy: {new_proxy['host']} for FINAL step")
            
            # Quit current driver
            self.driver.quit()
            time.sleep(2)
            
            # Create new driver with different proxy
            self.driver = self.create_driver_with_proxy(new_proxy)
            if not self.driver:
                print("❌ Failed to create new driver")
                return False
            
            self.wait = WebDriverWait(self.driver, 20)
            self.current_proxy = new_proxy
            
            # Navigate to appointment-booking page
            target_url = "https://visas-de.tlscontact.com/en-us/appointment-booking"
            print(f"🔗 Navigating with new proxy to: {target_url}")
            self.driver.get(target_url)
            time.sleep(3)
            
            # Restore cookies
            for cookie in cookies_before:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(5)
            
            # Check if we're successfully on the page
            current_url = self.driver.current_url
            print(f"📍 After cookie restore: {current_url}")
            
            if self.is_blocked():
                print("🚫 Still blocked after proxy switch")
                return False
            
            print("✅ Successfully navigated to final page with new proxy!")
            return True
            
        except Exception as e:
            print(f"❌ Proxy switch error: {e}")
            return False


def main():
    bot = TLSBot()
    bot.run()
    
if __name__ == "__main__":
    main()

