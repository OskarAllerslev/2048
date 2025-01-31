import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class Simple2048Bot:
    def __init__(self):
        # Launch Chrome and go to the official 2048 site
        self.driver = webdriver.Chrome()
        self.driver.get("https://play2048.co/")
        time.sleep(2)  # Let it load

        # We'll repeatedly press these four moves in a cycle
        self.moves = [Keys.ARROW_UP, Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT]

    def is_game_over(self):
        """
        Check if 'Game over!' text is displayed.
        On play2048.co, a 'div.game-message.game-over' appears with text 'Game over!'
        """
        try:
            game_message = self.driver.find_element(By.CSS_SELECTOR, ".game-message.game-over")
            if game_message.is_displayed():
                return True
        except NoSuchElementException:
            pass
        return False

    def play(self):
        """
        Main loop:
          1) Press Up, Right, Down, Left in a cycle.
          2) Check if game is over.
          3) Continue until game is over.
        """
        move_index = 0

        while True:
            if self.is_game_over():
                print("Game Over!")
                break

            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(self.moves[move_index])

            move_index = (move_index + 1) % len(self.moves)
            time.sleep(0.1)  # A small pause so we can see the moves

        time.sleep(3)
        self.driver.quit()


if __name__ == "__main__":
    bot = Simple2048Bot()
    bot.play()
