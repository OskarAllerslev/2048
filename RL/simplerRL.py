import gymnasium as gym
import gym_2048
from stable_baselines3 import PPO

# Create the 2048 environment
env = gym.make('2048-v0')

# Initialize the PPO model
model = PPO('MlpPolicy', env, verbose=1)

# Train the model
model.learn(total_timesteps=100000)

# Save the trained model
model.save('ppo_2048_model')

# To use the trained model later:
# model = PPO.load('ppo_2048_model')

# Evaluate the trained model
obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()
