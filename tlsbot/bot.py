
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


class TLSBot:
    
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    LOGIN_URL = os.getenv("LOGIN_URL")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    NO_SLOT_CHANNEL_ID = os.getenv("NO_SLOT_CHANNEL_ID")
    CALENDAR_CHANNEL_ID = os.getenv("CALENDAR_CHANNEL_ID")
    
    # Add proxy settings
    PROXY_HOST = '198.23.239.134'  
    PROXY_PORT = '6540'  
    PROXY_USER = 'dfbhwtck' 
    PROXY_PASS = '16lu6q7n6w2m'

    def cleanup_chrome_processes(self):
        """Kill any existing Chrome processes"""
        import subprocess
        try:
            subprocess.run(["pkill", "-f", "chrome"], check=False)
            subprocess.run(["pkill", "-f", "chromium"], check=False)
            subprocess.run(["pkill", "-f", "chromedriver"], check=False)
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def __init__(self):
        self.cleanup_chrome_processes()  # Clean up before starting
        time.sleep(2)  # Wait a moment
        self.driver = self.setup_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Fix user data directory issue
        import tempfile
        import uuid
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}/{uuid.uuid4()}")
        chrome_options.add_argument("--remote-debugging-port=0")
        
        # Create proxy auth extension
        if self.PROXY_HOST and self.PROXY_PORT and self.PROXY_USER and self.PROXY_PASS:
            proxy_host = self.PROXY_HOST.strip()
            proxy_port = self.PROXY_PORT.strip()
            proxy_user = self.PROXY_USER.strip()
            proxy_pass = self.PROXY_PASS.strip()
            
            # Create a simple proxy extension
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            
            background_js = f"""
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{proxy_host}",
                        port: parseInt({proxy_port})
                    }},
                    bypassList: ["localhost"]
                }}
            }};

            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            function callbackFn(details) {{
                return {{
                    authCredentials: {{
                        username: "{proxy_user}",
                        password: "{proxy_pass}"
                    }}
                }};
            }}

            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """
            
            # Create extension directory
            import os
            extension_dir = f"{temp_dir}/proxy_auth_extension"
            os.makedirs(extension_dir, exist_ok=True)
            
            # Write extension files
            with open(f"{extension_dir}/manifest.json", "w") as f:
                f.write(manifest_json)
            
            with open(f"{extension_dir}/background.js", "w") as f:
                f.write(background_js)
            
            # Load extension
            chrome_options.add_argument(f"--load-extension={extension_dir}")
            print(f"🔧 Created proxy auth extension at: {extension_dir}")
        
        # Alternative: Try without auth first
        elif self.PROXY_HOST and self.PROXY_PORT:
            proxy_host = self.PROXY_HOST.strip()
            proxy_port = self.PROXY_PORT.strip()
            chrome_options.add_argument(f"--proxy-server=http://{proxy_host}:{proxy_port}")
            print(f"🔧 Using proxy without auth: http://{proxy_host}:{proxy_port}")
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        import random
        chosen_ua = random.choice(user_agents)
        chrome_options.add_argument(f"--user-agent={chosen_ua}")
        
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Wait a moment for extension to load
            time.sleep(3)
            
            return driver
            
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            raise

    def add_stealth_measures(self):
        """Add additional anti-detection measures"""
        # Random delays between actions
        import random
        time.sleep(random.uniform(2, 5))
        
        # Simulate human-like mouse movements
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            # Move mouse to random positions
            for _ in range(3):
                x = random.randint(100, 500)
                y = random.randint(100, 400)
                actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    def login(self):
        self.driver.get(self.LOGIN_URL)
        time.sleep(5)

        try:
            # Debug: Print initial page info
            print(f"Initial page title: {self.driver.title}")
            print(f"Initial URL: {self.driver.current_url}")
            
            # Find and fill login form
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
                    
                    # Find and click login button
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
                        login_button.click()
                        print("🔄 Login button clicked, waiting for redirect...")
                        
                        # Wait for auth-callback
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.url_contains("auth-callback")
                            )
                            print(f"📍 Reached auth-callback: {self.driver.current_url}")
                        except:
                            print("⚠️ Didn't reach auth-callback")
                        
                        # Now wait for final redirect to dashboard
                        print("🔄 Waiting for final redirect to dashboard...")
                        time.sleep(10)  # Give time for redirect
                        
                        # Check multiple possible success indicators
                        current_url = self.driver.current_url
                        page_title = self.driver.title
                        
                        print(f"📍 Final URL: {current_url}")
                        print(f"📄 Final page title: {page_title}")
                        
                        # Success indicators
                        success_indicators = [
                            "travel-groups" in current_url.lower(),
                            "dashboard" in current_url.lower(),
                            "appointment" in current_url.lower(),
                            "booking" in current_url.lower(),
                            "travel groups" in page_title.lower(),
                            "dashboard" in page_title.lower(),
                            "appointment" in page_title.lower()
                        ]
                        
                        # Check for Select buttons (indicates we're on the right page)
                        has_select_button = False
                        try:
                            select_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')] | //a[contains(text(), 'Select')] | //input[@value='Select']")
                            if select_buttons:
                                has_select_button = True
                                print(f"✅ Found {len(select_buttons)} Select button(s)")
                        except:
                            pass
                        
                        # Check for error indicators
                        error_indicators = [
                            "error" in current_url.lower(),
                            "login" in current_url.lower() and "auth-callback" not in current_url.lower(),
                            "invalid" in page_title.lower(),
                            "error" in page_title.lower()
                        ]
                        
                        # If still on auth-callback, try to find a continue/redirect element
                        if "auth-callback" in current_url:
                            print("🔄 Still on auth-callback, looking for redirect elements...")
                            try:
                                # Look for any auto-redirect elements or continue buttons
                                continue_elements = self.driver.find_elements(By.XPATH, 
                                    "//a[contains(text(), 'Continue')] | //button[contains(text(), 'Continue')] | " +
                                    "//a[contains(text(), 'Proceed')] | //button[contains(text(), 'Proceed')] | " +
                                    "//a[contains(@href, 'travel')] | //a[contains(@href, 'dashboard')]"
                                )
                                if continue_elements:
                                    print(f"🔗 Found {len(continue_elements)} potential redirect elements")
                                    # Click the first one
                                    self.driver.execute_script("arguments[0].click();", continue_elements[0])
                                    time.sleep(5)
                                    print(f"📍 After click URL: {self.driver.current_url}")
                            except Exception as e:
                                print(f"⚠️ Error looking for redirect elements: {e}")
                            
                            # Check page source for auto-redirect script
                            try:
                                page_source = self.driver.page_source
                                if "window.location" in page_source or "redirect" in page_source.lower():
                                    print("🔄 Page contains redirect script, waiting...")
                                    time.sleep(10)
                                    print(f"📍 After waiting URL: {self.driver.current_url}")
                            except:
                                pass
                        
                        # Final verification
                        final_url = self.driver.current_url
                        final_title = self.driver.title
                        
                        if any(success_indicators) or has_select_button or "travel" in final_url.lower():
                            print("✅ Login appears successful!")
                            return True
                        elif any(error_indicators):
                            print("❌ Login failed - error detected")
                            return False
                        elif "auth-callback" in final_url:
                            print("⚠️ Still on auth-callback page - login may be incomplete")
                            # Save screenshot for debugging
                            try:
                                self.driver.save_screenshot("/tmp/auth_callback_stuck.png")
                                print("📸 Screenshot saved: /tmp/auth_callback_stuck.png")
                            except:
                                pass
                            return False
                        else:
                            print("🤔 Uncertain login status, proceeding anyway...")
                            return True
            
            return False
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def click_first_select(self):

        buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')]")
        if buttons:
            try:
                self.driver.execute_script("arguments[0].click();", buttons[0])
                time.sleep(3)
                print("✅ 'Select' düyməsi klikləndi (JS click)!")
                return True
            except Exception as e:
                print(f"⚠️ Select klik xətası: {e}")
        print("❌ 'Select' düyməsi tapılmadı.")
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
            start_text = "We currently don’t have any appointment slots available."
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


    def run(self):
        try:
            if self.login():
                if self.click_first_select():
                    if self.click_continue():
                        self.wait_final_page()
        except Exception as e:
            print(f"⚠️ Bot çalışarkən istisna: {e}")
        finally:
            try:
                self.driver.quit()
            except Exception:
                print(f"⚠️ Driver bağlanarkən xəta: {e}")


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


def main():
    bot = TLSBot()
    bot.run()
    
if __name__ == "__main__":
    main()

