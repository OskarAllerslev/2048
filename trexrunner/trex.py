import time
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image

class ChromeDinoBot:
    def __init__(self):
        # Launch the Chrome browser
        self.driver = webdriver.Chrome()
        # Go to a T-Rex game clone that runs in HTML/Canvas
        self.driver.get("https://trex-runner.com/")  
        time.sleep(2)

        # Grab the canvas element where the game is drawn
        self.canvas = self.driver.find_element(By.CLASS_NAME, "runner-canvas")

        # Dimensions – from the site’s runner-canvas (600x150 typically)
        self.WIDTH = 600
        self.HEIGHT = 150

        # Where to look for obstacles, relative to T-Rex’s likely position
        # For example, look ahead in a rectangle x=[50..80], y=[90..110]
        self.check_x_start = 50
        self.check_x_end = 80
        self.check_y_start = 90
        self.check_y_end = 110

    def start_game(self):
        """
        Press SPACE to start or restart the game.
        """
        body_elem = self.driver.find_element(By.TAG_NAME, "body")
        body_elem.send_keys(Keys.SPACE)
        time.sleep(1)

    def is_game_over(self):
        """
        The game sets the 'class' on the canvas or runner
        or changes the T-Rex sprite to 'dead' if you lose.
        Checking a quick way to see if T-Rex is dead:
        - Sometimes the page adds a 'crashed' class to the body or canvas
        - We can also do a pixel check (if T-Rex sprite changes).
        Here, we do a pixel check in an area where the 'GAME OVER' text appears.
        """
        screenshot = self._get_canvas_screenshot()
        # 'GAME OVER' text often appears around top center, 
        # let's check a small region in the top middle
        # If it's black text on white background, we can detect difference
        # In the actual clone site, it might say "HI 00000" as well. We'll just do a rough check:
        # If we see a large patch of black, it's likely the game over text.
        # This is just an example check; you can do more robust checks as needed.
        # We'll just sample a pixel in the region [280, 22].
        sample_x = 280
        sample_y = 22

        if sample_x < screenshot.width and sample_y < screenshot.height:
            pixel = screenshot.getpixel((sample_x, sample_y))
            # pixel is (R, G, B)
            # If it's fairly dark, we assume "GAME OVER" text
            if sum(pixel) < 200:  # a rough threshold for "dark"
                return True

        return False

    def jump(self):
        """
        Press the UP arrow key to jump.
        """
        body_elem = self.driver.find_element(By.TAG_NAME, "body")
        body_elem.send_keys(Keys.ARROW_UP)

    def duck(self, ducking=True):
        """
        Press or release the DOWN arrow key to duck.
        (You might or might not use this, depending on obstacles.)
        """
        body_elem = self.driver.find_element(By.TAG_NAME, "body")
        if ducking:
            body_elem.send_keys(Keys.ARROW_DOWN)
        else:
            # There's no direct "release key" in Selenium, 
            # so we typically just do a short press or rely on game logic.
            pass

    def see_obstacle(self):
        """
        Returns True if there is a dark pixel in the region where 
        obstacles appear in front of T-Rex.
        """
        screenshot = self._get_canvas_screenshot()

        # Check the bounding box x=[check_x_start..check_x_end], y=[check_y_start..check_y_end]
        for x in range(self.check_x_start, self.check_x_end):
            for y in range(self.check_y_start, self.check_y_end):
                pixel = screenshot.getpixel((x, y))
                # If pixel is fairly dark => likely obstacle
                if sum(pixel) < 200:  # sum(R,G,B) < 200 => dark
                    return True
        return False

    def _get_canvas_screenshot(self):
        """
        Returns a PIL Image of the <canvas> contents.
        We'll ask Selenium for a screenshot of the full page
        and then crop to the canvas area.
        """
        png_data = self.driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png_data))

        # Get canvas location on page
        location = self.canvas.location  # dict of {'x':..., 'y':...}
        size = self.canvas.size  # dict of {'width':..., 'height':...}
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        # Crop to just the game canvas
        im = im.crop((left, top, right, bottom))
        return im

    def play(self):
        """
        Main loop:
        1) Start game
        2) While not game-over:
           - Check for obstacle
           - If obstacle => jump
           - Sleep briefly => continue
        """
        self.start_game()

        while True:
            if self.is_game_over():
                print("Game Over!")
                break

            if self.see_obstacle():
                self.jump()

            # Delay so we don't hammer the CPU too hard
            time.sleep(0.05)

        # Optionally close the browser
        time.sleep(3)
        self.driver.quit()


if __name__ == "__main__":
    bot = ChromeDinoBot()
    bot.play()
