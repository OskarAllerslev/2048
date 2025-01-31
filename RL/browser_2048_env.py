import gymnasium as gym
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class Browser2048Env(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(
            low=0, high=2048, shape=(4, 4), dtype=np.int32
        )

        self.driver = webdriver.Chrome()
        self.driver.get("https://2048.ninja")
        time.sleep(2)
        self.body_elem = self.driver.find_element(By.TAG_NAME, "body")

        self.ACTION_MAP = {
            0: Keys.ARROW_UP,
            1: Keys.ARROW_DOWN,
            2: Keys.ARROW_LEFT,
            3: Keys.ARROW_RIGHT
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Reload the game to reset state
        self.driver.refresh()
        time.sleep(2)

        obs = self._get_board()
        info = {}
        return obs, info

    def step(self, action):
        self._perform_action(action)
        new_board = self._get_board()

        # If 'Game Over' is displayed, we treat it as "terminated"
        game_over = self._is_game_over()
        reward = self._calculate_reward(new_board)

        terminated = game_over
        truncated = False  # For 2048, we typically don't have a time-limit or forced cut

        return new_board, reward, terminated, truncated, {}

    def _perform_action(self, action):
        if action in self.ACTION_MAP:
            self.body_elem.send_keys(self.ACTION_MAP[action])
            time.sleep(0.1)

    def _get_board(self):
        tiles = self.driver.find_elements(By.CLASS_NAME, "tile")
        board = np.zeros((4, 4), dtype=int)

        for tile in tiles:
            class_str = tile.get_attribute("class")
            classes = class_str.split()
            value, row, col = 0, 0, 0

            for cl in classes:
                if cl.startswith("tile-") and "tile-position" not in cl:
                    try:
                        value = int(cl.split("-")[1])
                    except ValueError:
                        pass
                if cl.startswith("tile-position-"):
                    parts = cl.split("-")
                    try:
                        row, col = int(parts[1]) - 1, int(parts[2]) - 1
                    except ValueError:
                        pass

            if 0 <= row < 4 and 0 <= col < 4:
                board[row, col] = max(board[row, col], value)

        return board

    def _is_game_over(self):
        try:
            game_message = self.driver.find_element(By.CLASS_NAME, "game-message")
            return game_message.is_displayed()
        except:
            return False

    def _calculate_reward(self, board):
        # A simple (not necessarily optimal) reward: sum of tiles
        return np.sum(board)

    def render(self, mode="human"):
        print(self._get_board())

    def close(self):
        self.driver.quit()
