from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque
import time

class SnakeBot:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://playsnake.org/")
        
        # Game grid dimensions
        self.grid_width = 21
        self.grid_height = 15
        
        # Initialize tracking variables
        self.head = (10, 2)
        self.direction = "DOWN"
        self.last_score = 0

    def start_game(self):
        # Select Python level (hardest)
        level_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//p[@data-level='2']"))
        )
        level_button.click()
        
        # Wait for game to start
        WebDriverWait(self.driver, 10).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "countdown"))
        )

    def get_game_state(self):
        cells = self.driver.find_elements(By.CLASS_NAME, "cell")
        snake = []
        food = None
        
        for idx, cell in enumerate(cells):
            classes = cell.get_attribute("class")
            x = idx % self.grid_width
            y = idx // self.grid_width
            
            if "snake" in classes:
                snake.append((x, y))
            if "food" in classes:
                food = (x, y)
        
        return snake, food

    def find_path(self, start, target, obstacles):
        queue = deque()
        queue.append(start)
        visited = {start: None}
        directions = [(0, -1, "UP"), (0, 1, "DOWN"), 
                     (-1, 0, "LEFT"), (1, 0, "RIGHT")]

        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                while current != start:
                    path.append(current)
                    current = visited[current]
                return path[::-1]
            
            for dx, dy, dir_name in directions:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                
                if (0 <= nx < self.grid_width and 
                    0 <= ny < self.grid_height and 
                    next_pos not in obstacles and 
                    next_pos not in visited):
                    
                    visited[next_pos] = current
                    queue.append(next_pos)
        
        return None  # No path found

    def get_safe_direction(self, obstacles):
        directions = []
        x, y = self.head
        
        possible_moves = [
            (x, y-1, "UP"),
            (x, y+1, "DOWN"),
            (x-1, y, "LEFT"),
            (x+1, y, "RIGHT")
        ]
        
        for nx, ny, dir_name in possible_moves:
            if (0 <= nx < self.grid_width and 
                0 <= ny < self.grid_height and 
                (nx, ny) not in obstacles and
                not self.is_opposite(dir_name)):
                directions.append(dir_name)
        
        return directions[0] if directions else None

    def is_opposite(self, new_dir):
        opposites = {"UP": "DOWN", "DOWN": "UP", 
                    "LEFT": "RIGHT", "RIGHT": "LEFT"}
        return new_dir == opposites.get(self.direction, "")

    def move(self, direction):
        key_mapping = {
            "UP": Keys.ARROW_UP,
            "DOWN": Keys.ARROW_DOWN,
            "LEFT": Keys.ARROW_LEFT,
            "RIGHT": Keys.ARROW_RIGHT
        }
        self.driver.find_element(By.TAG_NAME, "body").send_keys(key_mapping[direction])
        self.direction = direction

    def update_head_position(self):
        dx, dy = 0, 0
        if self.direction == "UP":
            dy = -1
        elif self.direction == "DOWN":
            dy = 1
        elif self.direction == "LEFT":
            dx = -1
        elif self.direction == "RIGHT":
            dx = 1
        
        self.head = (self.head[0] + dx, self.head[1] + dy)

    def play(self):
        self.start_game()
        
        while True:
            snake, food = self.get_game_state()
            current_score = int(self.driver.find_element(By.CLASS_NAME, "score").text)
            
            # Check if game over
            if current_score == self.last_score:
                print("Game Over - Restarting...")
                self.driver.find_element(By.CLASS_NAME, "board").click()
                self.start_game()
                self.head = (10, 2)
                self.direction = "DOWN"
                self.last_score = 0
                continue
            
            self.last_score = current_score
            obstacles = set(snake)
            
            # Find path to food
            path = self.find_path(self.head, food, obstacles)
            
            if path:
                next_step = path[0]
                dx = next_step[0] - self.head[0]
                dy = next_step[1] - self.head[1]
                
                if dx == 1:
                    new_dir = "RIGHT"
                elif dx == -1:
                    new_dir = "LEFT"
                elif dy == 1:
                    new_dir = "DOWN"
                else:
                    new_dir = "UP"
            else:
                # Find safe move if no path to food
                new_dir = self.get_safe_direction(obstacles)
                if not new_dir:
                    new_dir = self.direction  # Continue current direction

            # Prevent 180-degree turns
            if not self.is_opposite(new_dir):
                self.move(new_dir)
                self.update_head_position()
            
            time.sleep(0.05)  # Adjust based on game speed

if __name__ == "__main__":
    bot = SnakeBot()
    try:
        bot.play()
    except KeyboardInterrupt:
        bot.driver.quit()