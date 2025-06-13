
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
    PROXY_HOST = 'https://proxy2.webshare.io/'  # e.g., "proxy.example.com"
    PROXY_PORT = '198.23.239.134'  # e.g., "8080"
    PROXY_USER = 'dfbhwtck ' # if auth required
    PROXY_PASS = '16lu6q7n6w2m ' # if auth required

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
        chrome_options.add_argument("--start-maximized")
        
        # Fix user data directory issue
        import tempfile
        import uuid
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}/{uuid.uuid4()}")
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Add residential proxy or rotating proxy
        if self.PROXY_HOST and self.PROXY_PORT:
            # Extract hostname from URL if it contains protocol
            proxy_host = self.PROXY_HOST
            if proxy_host.startswith('http://') or proxy_host.startswith('https://'):
                from urllib.parse import urlparse
                parsed = urlparse(proxy_host)
                proxy_host = parsed.hostname
            
            if self.PROXY_USER and self.PROXY_PASS:
                proxy = f"{self.PROXY_USER}:{self.PROXY_PASS}@{proxy_host}:{self.PROXY_PORT}"
            else:
                proxy = f"{proxy_host}:{self.PROXY_PORT}"
            
            chrome_options.add_argument(f"--proxy-server=http://{proxy}")
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        import random
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
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
        time.sleep(5)  # Increase wait time

        try:
            # Debug: Print page info
            print(f"Page title: {self.driver.title}")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if we need to handle any redirects or additional steps
            # Sometimes auth pages have multiple steps
            
            # Try to find the email field with different methods
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
                        # Print page source to debug
                        print("Page source (first 1000 chars):")
                        print(self.driver.page_source[:1000])
                        return False
            
            if email_field:
                email_field.send_keys(self.EMAIL)
                time.sleep(2)
                
                # Try to find password field
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
                            print("Password field not found")
                            return False
                
                if password_field:
                    password_field.send_keys(self.PASSWORD)
                    time.sleep(2)
                    
                    # Try to find login button
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
                                print("Login button not found")
                                return False
                    
                    if login_button:
                        login_button.click()
                        time.sleep(5)
                        
                        # Rest of your login verification logic...
                        print(f"After login URL: {self.driver.current_url}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Giriş zamanı xəta: {e}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            # Save screenshot for debugging
            try:
                self.driver.save_screenshot("/tmp/login_error.png")
                print("Screenshot saved to /tmp/login_error.png")
            except:
                pass
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

