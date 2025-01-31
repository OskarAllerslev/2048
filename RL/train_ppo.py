from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from browser_2048_env import Browser2048Env
from tqdm import tqdm

class TQDMProgressBarCallback(BaseCallback):
    def __init__(self, total_timesteps, verbose=0):
        super().__init__(verbose)
        self.total_timesteps = total_timesteps
        self.pbar = None
        self.start_timesteps = 0

    def _on_training_start(self):
        self.start_timesteps = self.model.num_timesteps
        self.pbar = tqdm(total=self.total_timesteps, desc="Training Progress")

    def _on_step(self):
        current_progress = self.model.num_timesteps - self.start_timesteps
        self.pbar.n = current_progress
        self.pbar.refresh()
        if current_progress >= self.total_timesteps:
            return False
        return True

    def _on_training_end(self):
        self.pbar.close()

env = Browser2048Env()
model = PPO("MlpPolicy", env, verbose=1)

progress_callback = TQDMProgressBarCallback(total_timesteps=200)
model.learn(total_timesteps=200, callback=progress_callback)

model.save("ppo_2048_browser")
env.close()
