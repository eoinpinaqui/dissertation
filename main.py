from game_environment.game import Game
from pynput.keyboard import Listener
from game_environment.game_constants import *
from random import randint

env = Game()
obs = env.reset()
done = False
total_reward = 0
action = DO_NOTHING


def press(key):
    global action
    if 'char' in dir(key):
        if key.char == 'w': action = ACCELERATE
        if key.char == 's': action = DECELERATE
        if key.char == 'a': action = TURN_LEFT
        if key.char == 'd': action = TURN_RIGHT
        if key.char == 'm': action = FIRE_MISSILE
        if key.char == 'n': action = CHANGE_SHIP
        if key.char == 'q': action = SPAWN_SCOUT
        if key.char == 'e': action = SPAWN_GUNNER
        if key.char == 'r': action = SPAWN_TANK


def release(key):
    global action
    action = DO_NOTHING


Listener(on_press=press, on_release=release).start()
while not done:
    action1 = randint(0, 9)
    action2 = randint(0, 9)
    action3 = randint(0, 9)
    action4 = randint(0, 9)
    obs, reward, done, info = env.step([action1, action2, action3, action4])
    total_reward += reward
    env.render()
    if done:
        break

env.close()
print(total_reward)
