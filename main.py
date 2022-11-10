from game_environment.single_player import SinglePlayerGame
from pynput.keyboard import Listener

env = SinglePlayerGame()
obs = env.reset()
done = False
total_reward = 0
action = 4


def press(key):
    global action
    if 'char' in dir(key):
        if key.char == 'w': action = 2
        if key.char == 's': action = 3
        if key.char == 'a': action = 0
        if key.char == 'd': action = 1


def release(key):
    global action
    action = 4


Listener(on_press=press, on_release=release).start()

while not done:
    obs, reward, done, info = env.step(action)
    total_reward += reward
    env.render()
    if done:
        break

env.close()
print(total_reward)
