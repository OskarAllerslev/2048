# play_trained.py
from stable_baselines3 import PPO
from browser_2048_env import Browser2048Env

model = PPO.load("ppo_2048_browser")
env = Browser2048Env()

obs = env.reset()
done = False

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()  # Print the board state

print("Game Over!")
env.close()
