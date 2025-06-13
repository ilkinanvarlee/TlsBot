
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


    def __init__(self):
        self.driver = self.setup_driver()
        self.wait = WebDriverWait(self.driver, 20)


    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    def login(self):
        self.driver.get(self.LOGIN_URL)
        time.sleep(3)

        try:
            # Fill login form
            self.wait.until(EC.visibility_of_element_located((By.ID, "email-input-field"))).send_keys(self.EMAIL)
            self.wait.until(EC.visibility_of_element_located((By.ID, "password-input-field"))).send_keys(self.PASSWORD)
            self.wait.until(EC.element_to_be_clickable((By.ID, "btn-login"))).click()
            
            # Wait for redirect after login (auth-callback)
            print("Waiting for auth redirect...")
            time.sleep(5)  # Give more time for redirect
            
            # Wait for final redirect to dashboard/travel-groups
            # Try to wait for either travel-groups URL or specific elements that indicate successful login
            try:
                # Option 1: Wait for travel-groups in URL
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "travel-groups" in driver.current_url
                )
                print("✅ Giriş uğurlu oldu! (travel-groups URL)")
                print("Final URL:", self.driver.current_url)
                return True
                
            except TimeoutException:
                # Option 2: If travel-groups URL doesn't appear, check for Select buttons or other indicators
                try:
                    # Wait for Select button to appear (indicates we're on the right page)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Select')]"))
                    )
                    print("✅ Giriş uğurlu oldu! (Select button found)")
                    print("Current URL:", self.driver.current_url)
                    return True
                    
                except TimeoutException:
                    # Option 3: Check for any other indicators of successful login
                    try:
                        # Look for common dashboard elements
                        WebDriverWait(self.driver, 5).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CLASS_NAME, "dashboard")),
                                EC.presence_of_element_located((By.CLASS_NAME, "travel-group")),
                                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Travel Groups')]")),
                            )
                        )
                        print("✅ Giriş uğurlu oldu! (Dashboard elements found)")
                        print("Current URL:", self.driver.current_url)
                        return True
                        
                    except TimeoutException:
                        print("❌ Giriş uğursuz oldu - expected elements not found")
                        print("Current URL:", self.driver.current_url)
                        # Print page source for debugging
                        print("Page title:", self.driver.title)
                        return False
                
        except Exception as e:
            print(f"❌ Giriş zamanı xəta: {e}")
            print("Current URL:", self.driver.current_url)
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

