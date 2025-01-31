import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


class CookieClickerBot:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://orteil.dashnet.org/cookieclicker/")
        # Wait a bit for the game to load
        time.sleep(5)

    def setup_game(self):
        """
        Close any initial popups or select a language if needed.
        """
        # The game might show a language selection screen. Let's pick English if present.
        try:
            lang_select = self.driver.find_element(By.ID, "langSelect-EN")
            lang_select.click()
            time.sleep(2)
        except NoSuchElementException:
            pass

        # Sometimes there is a "Got it!" cookie policy button. Let's try to close it if present.
        try:
            cookie_banner = self.driver.find_element(By.CSS_SELECTOR, "div.cc_banner-wrapper")
            got_it_button = cookie_banner.find_element(By.CSS_SELECTOR, "a.cc_btn_accept_all")
            got_it_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass

        # Wait a bit more for the main interface to finalize
        time.sleep(2)

    def get_cookie_count(self):
        """
        Parse the cookie count from the top info bar.
        """
        cookies_elem = self.driver.find_element(By.ID, "cookies")
        # Example text: "123 cookies"
        text = cookies_elem.text
        # Some versions might show "123 cookies per second: 5.0"
        # We'll extract the first number
        match = re.search(r"([0-9,]+)", text)
        if match:
            count_str = match.group(1)
            return int(count_str.replace(",", ""))  # remove commas, convert to int
        return 0

    def click_big_cookie(self, times=50):
        """
        Click the big cookie multiple times.
        """
        big_cookie = self.driver.find_element(By.ID, "bigCookie")
        for _ in range(times):
            big_cookie.click()

    def buy_upgrades(self):
        """
        Buy any upgrades (top row icons) if they are available.
        """
        upgrade_icons = self.driver.find_elements(By.CSS_SELECTOR, "# upgrades .crate.upgrade.enabled")
        for icon in upgrade_icons:
            try:
                icon.click()
            except (ElementClickInterceptedException, NoSuchElementException):
                pass

    def buy_buildings(self):
        """
        Buy the most expensive affordable building.
        Buildings have IDs like "product0", "product1", ...
        We'll try from the bottom up (most expensive first).
        """
        # The base game has building IDs from 0 up to ~ 19 (Cursor, Grandma, Farm, etc.)
        # Let’s see how many building elements are present
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, "#products .product.unlocked.enabled")
        # That returns only "buyable" (unlocked & enabled) buildings
        # They might not be sorted by price. Typically, building #0 is cheapest, highest is the priciest.
        # So we sort by product ID descending (largest ID first => most expensive building).
        buyables = []
        for elem in product_elements:
            # each building has an ID like "product0", "product1", ...
            product_id = elem.get_attribute("id")
            # Extract the numeric part
            num_str = product_id.replace("product", "")
            if num_str.isdigit():
                buyables.append((int(num_str), elem))

        # Sort descending by product ID
        buyables.sort(key=lambda x: x[0], reverse=True)

        # Try to click the most expensive first
        for _, building_elem in buyables:
            try:
                building_elem.click()
                # If we can afford it, it will buy. If not, it remains "enabled"? 
                # In practice, if it's "enabled," we can afford at least one.
                # Let's break after the first purchase
                break
            except ElementClickInterceptedException:
                # If a random popup or something blocks, ignore
                pass
            except NoSuchElementException:
                pass

    def run(self):
        self.setup_game()

        # Start an infinite loop or run for X iterations
        last_buy_time = time.time()
        buy_interval = 5.0  # Every 5 seconds, try buying

        while True:
            # Click the cookie a bunch
            self.click_big_cookie(times=50)

            # Periodically attempt to buy
            if time.time() - last_buy_time > buy_interval:
                self.buy_upgrades()
                self.buy_buildings()
                last_buy_time = time.time()

            cookie_count = self.get_cookie_count()
            print(f"Cookie count: {cookie_count}")

            # Sleep a short time so we don't hammer CPU
            time.sleep(0.5)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    bot = CookieClickerBot()
    bot.run()
    # Will run indefinitely. Press Ctrl+C to stop.
    
