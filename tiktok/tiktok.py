import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

class TikTokFullVideoWatcher:
    def __init__(self, scroll_pause=2):
        """
        :param scroll_pause: Number of seconds to wait after we scroll to the next video.
        """
        self.scroll_pause = scroll_pause
        # Initialize WebDriver (Chrome in this example).
        self.driver = webdriver.Chrome()

    def open_tiktok(self, url="https://www.tiktok.com/foryou"):
        """
        Navigate to TikTok's web feed (e.g. /foryou).
        You may need to log in or handle pop-ups if you want a full feed.
        """
        self.driver.get(url)
        time.sleep(5)  # Let the page load
        self.close_popups()

    def close_popups(self):
        """
        Attempt to close or bypass any cookie/login pop-ups.
        Adjust if the site changes its design.
        """
        # Example: look for 'Accept' / 'Reject' cookie buttons
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                txt = btn.text.strip().lower()
                if "accept" in txt or "reject" in txt or "agree" in txt:
                    btn.click()
                    time.sleep(1)
                    break
        except NoSuchElementException:
            pass

        # Sometimes a login overlay might appear. Try closing if there's an 'X' or 'Log in later' button.
        # This is site/version-specific, so you may need to refine.
        try:
            close_btn = self.driver.find_element(By.XPATH, "//button[contains(@class,'close')]")
            close_btn.click()
        except NoSuchElementException:
            pass

    def get_visible_video(self):
        """
        Return the first <video> element on the page.
        In theory, the "top" or "centered" video is the currently playing one.
        Adjust logic if multiple are visible.
        """
        try:
            # Simple approach: the first <video> in the DOM
            video_elem = self.driver.find_element(By.CSS_SELECTOR, "video:nth-of-type(1)")
            return video_elem
        except NoSuchElementException:
            return None

    def watch_video_once(self, video_elem):
        """
        Attempt to watch `video_elem` for its full duration once.
        If we can't read duration (e.g. crossOrigin locked or Infinity), we use a fallback.
        """
        default_watch_time = 10.0  # fallback if reading .duration fails

        # Try reading the HTMLMediaElement.duration via JS
        try:
            duration = self.driver.execute_script("return arguments[0].duration", video_elem)
            # If duration is 0 or infinite, fallback
            if not duration or duration == float('inf'):
                duration = default_watch_time
        except WebDriverException:
            # If we can't read property for some reason
            duration = default_watch_time

        print(f"Watching video for {duration:.2f} seconds...")
        time.sleep(duration + 1)  # watch the clip once, plus a small buffer

    def scroll_to_next(self):
        """
        Scroll once, so the next video is in view.
        Some users prefer PAGE_DOWN or ARROW_DOWN. 
        Alternatively, we can do a small JS scroll to ensure next video appears in center.
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(self.scroll_pause)

    def run(self):
        self.open_tiktok()

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
    bot = TikTokFullVideoWatcher(scroll_pause=2)
    bot.run()
