import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    ElementClickInterceptedException,
)


class TikTokFullVideoWatcher:
    def __init__(self, scroll_pause=2, username=None, password=None):
        """
        :param scroll_pause: Number of seconds to wait after we scroll to the next video.
        :param username: TikTok username/email for login (optional)
        :param password: TikTok password (optional)
        """
        self.scroll_pause = scroll_pause
        self.username = 'allerslev0'

        # Initialize WebDriver (Chrome in this example).
        self.driver = webdriver.Chrome()

    def open_tiktok(self, url="https://www.tiktok.com/foryou"):
        """
        Navigate to TikTok's web feed (e.g., /foryou).
        If we have username/password, attempt to log in.
        """
        self.driver.get(url)
        time.sleep(5)  # Let the page load
        self.close_popups()

        # If credentials provided, try logging in
        if self.username and self.password:
            self.login()

    def close_popups(self):
        """
        Attempt to close or bypass any cookie/login pop-ups.
        Adjust if the site changes its design.
        """
        # 1) Look for 'Accept' / 'Reject' / 'Agree' cookie buttons
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                txt = btn.text.strip().lower()
                if any(keyword in txt for keyword in ["accept", "reject", "agree"]):
                    btn.click()
                    time.sleep(1)
                    break
        except NoSuchElementException:
            pass

        # 2) Sometimes a login overlay might appear. 
        #    Try closing if there's an 'X' or 'Log in later' button.
        #    This is site/version-specific, so you may need to refine.
        try:
            close_btn = self.driver.find_element(By.XPATH, "//button[contains(@class,'close')]")
            close_btn.click()
            time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            pass

    def login(self):
        """
        Attempt to log in using an email/username + password form.
        This may need updating depending on TikTok's current web UI.
        """
        try:
            # 1) Click the 'Log in' button or link if it's on the main page
            #    This might be a button with text 'Log in', or an icon, etc.
            #    Adjust the selector as necessary.
            login_buttons = self.driver.find_elements(By.XPATH, "//*[text()='Log in' or text()='Log in ']")
            if login_buttons:
                login_buttons[0].click()
                time.sleep(3)

            # 2) If there's a secondary step: 
            #    e.g., "Use phone / email / username" or "Continue with email"
            #    Adjust the text or class as needed.
            use_email_option = self.driver.find_element(
                By.XPATH, "//*[contains(text(),'Use phone / email / username')]"
            )
            use_email_option.click()
            time.sleep(2)

            # 3) Switch to 'Email/Username' tab if there's a separate tab
            #    Some flows have separate "Phone" vs. "Email/Username" tabs.
            #    Adjust as needed.
            email_tab = self.driver.find_element(
                By.XPATH, "//*[contains(text(),'Email/Username')]"
            )
            email_tab.click()
            time.sleep(2)

            # 4) Enter username/email
            username_input = self.driver.find_element(By.NAME, "username")
            username_input.send_keys(self.username)
            time.sleep(1)

            # 5) Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            time.sleep(1)

            # 6) Click the 'Log in' button
            login_submit_btn = self.driver.find_element(By.XPATH, "//button[contains(@class,'login-button')]")
            login_submit_btn.click()
            time.sleep(5)

            print("Login attempt completed. Check if logged in successfully.")
        except NoSuchElementException as e:
            print("Login elements not found. TikTok may have changed the UI or there's a captcha.")
            print(e)

    def get_visible_video(self):
        """
        Return the first <video> element on the page.
        In theory, the "top" or "centered" video is the currently playing one.
        Adjust logic if multiple are visible.
        """
        try:
            video_elem = self.driver.find_element(By.CSS_SELECTOR, "video:nth-of-type(1)")
            return video_elem
        except NoSuchElementException:
            return None

    def watch_video_once(self, video_elem):
        """
        Attempt to watch `video_elem` for its full duration once.
        If we can't read duration (e.g., crossOrigin locked or Infinity), we use a fallback.
        """
        default_watch_time = 10.0  # fallback if reading .duration fails
        try:
            duration = self.driver.execute_script("return arguments[0].duration", video_elem)
            if not duration or duration == float("inf"):
                duration = default_watch_time
        except WebDriverException:
            duration = default_watch_time

        print(f"Watching video for {duration:.2f} seconds...")
        time.sleep(duration + 1)  # watch the clip once, plus a small buffer

    def scroll_to_next(self):
        """
        Scroll once, so the next video is in view.
        Some users prefer PAGE_DOWN or ARROW_DOWN. 
        Alternatively, do a small JS scroll so next video is center screen.
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(self.scroll_pause)

    def run(self):
        self.open_tiktok("https://www.tiktok.com/foryou")

        while True:
            video_elem = self.get_visible_video()
            if not video_elem:
                print("No video found—maybe we've reached the end or need to log in.")
                break

            # Watch the first visible video once
            self.watch_video_once(video_elem)

            # Scroll to bring the next video into view
            self.scroll_to_next()

        print("Done watching videos. Closing.")
        time.sleep(3)
        self.driver.quit()


if __name__ == "__main__":
    # Provide your own username and password
    my_username = "your.tiktok.username"
    my_password = "your_tiktok_password"

    bot = TikTokFullVideoWatcher(
        scroll_pause=2,
        username=my_username,
        password=my_password
    )
    bot.run()
