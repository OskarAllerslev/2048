import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class FlappyBirdBot:
    def __init__(self):
        # Launch a new browser session
        self.driver = webdriver.Chrome()
        # Navigate to the Flappy Bird clone site
        self.driver.get("https://flappybird.io/")
        time.sleep(2)  # Let the page load

    def start_game(self):
        """
        Press SPACE once to start the game.
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SPACE)
        time.sleep(0.5)  # A short pause

    def is_game_over(self):
        """
        Check if 'Restart' button is visible in the DOM.
        Flappybird.io shows a 'Restart' button after you die.
        """
        try:
            restart_btn = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='restart']")
            if restart_btn.is_displayed():
                return True
        except NoSuchElementException:
            pass
        return False

    def keep_flapping(self):
        """
        Repeatedly press SPACE to keep the bird in the air.
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        # Press space every 0.15s
        while True:
            # If we detect 'Restart', game is over
            if self.is_game_over():
                print("Game Over!")
                break

            body.send_keys(Keys.SPACE)
            time.sleep(0.15)

    def run(self):
        """
        Overall control:
        1) Start game
        2) Keep flapping until game over
        3) Close
        """
        self.start_game()
        self.keep_flapping()
        time.sleep(2)
        self.driver.quit()

if __name__ == "__main__":
    bot = FlappyBirdBot()
    bot.run()
