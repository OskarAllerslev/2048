import time
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# 1. Define the URL of the 2048 game
#GAME_URL = "https://play2048.co/"
GAME_URL = "https://gabrielecirulli.github.io/2048/"

# 2. Set up Selenium (Chrome)
options = webdriver.ChromeOptions()
# Comment out headless if you actually want to see the browser window
# options.add_argument("--headless")  
driver = webdriver.Chrome(options=options)
driver.get(GAME_URL)

time.sleep(2)  # give browser a moment to load

# 3. Grab the main container (body) for sending keys
game_board = driver.find_element("tag name", "body")

# 4. Function to mimic human-like (random) delay
def get_human_like_delay():
    # mean=0.5s, std=0.05s but absolute value to avoid negative
    return abs(np.random.normal(loc=0.01, scale=0.05))

# 5. A simple “try up, else left, else right, else down” strategy
def make_move():
    """
    Attempt an 'UP' move first. If it doesn't change the board, try
    LEFT -> RIGHT -> DOWN, in that order, until you find a move that changes.
    This helps keep high-value tiles in a corner. 
    """
    move_order = [Keys.ARROW_UP, Keys.ARROW_LEFT, Keys.ARROW_RIGHT, Keys.ARROW_DOWN]
    
    # We'll attempt each move in sequence until something changes.
    # To detect change, we can read the text from the tile containers before and after.
    
    before_board = get_board_state()
    
    for move in move_order:
        game_board.send_keys(move)
        time.sleep(get_human_like_delay())
        
        after_board = get_board_state()
        
        # If board changed, break out of loop
        if after_board != before_board:
            break

def get_board_state():
    """
    Reads the current board tiles from the webpage and returns 
    a tuple of tile values (or any representation) so we can 
    detect if a move had any effect.
    """
    tiles = driver.find_elements("class name", "tile")
    print("DEBUG: Found", len(tiles), "tiles")


    
    # Each tile has classes like 'tile tile-2 tile-position-1-2 tile-new'
    # We can extract the 'tile-2' part to get the value:
    tile_values = []
    for t in tiles:
        class_str = t.get_attribute("class")
        # class_str might look like: "tile tile-4 tile-position-2-1 tile-merged"
        # We'll parse out the part that says tile-X
        for c in class_str.split():
            if c.startswith("tile-") and c != "tile-position" and c != "tile-new" and c != "tile-merged":
                # e.g. c = "tile-4"
                # Remove "tile-" to get just the number
                try:
                    val = int(c.split("-")[1])
                    tile_values.append(val)
                except:
                    pass
    # return a tuple so it's hashable/comparable
    return tuple(sorted(tile_values))

# 6. Main game loop
print("Starting 2048 bot. Press CTRL+C to stop.")

try:
    while True:
        make_move()
        
        # After each move or sequence, check if game is over
        # The game might declare "Game over!" or show a 'try again' button
        try:
            game_over_message = driver.find_element("class name", "game-message")
            if game_over_message.is_displayed():
                # If "Game over!" is displayed, attempt to click "Try again"
                print("Game Over! Restarting...")
                retry_button = driver.find_element("class name", "retry-button")
                retry_button.click()
                time.sleep(2)
        except NoSuchElementException:
            # Not over yet
            pass
        
        # add a short delay to avoid spamming
        time.sleep(get_human_like_delay())

except KeyboardInterrupt:
    print("Bot stopped by user.")

finally:
    driver.quit()
