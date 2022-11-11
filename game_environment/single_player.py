from gym import Env, spaces
from .game_constants import *
from .ship import Ship
from .missile import Missile
from shapely.geometry.polygon import Polygon
import numpy as np
import cv2
import math
import random


class SinglePlayerGame(Env):
    def __init__(self):
        super().__init__()

        # Define the observation space
        self.observation_shape = (GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS)
        self.structure = Polygon(
            [(0, 0), (GAME_WINDOW_WIDTH, 0), (GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT), (0, GAME_WINDOW_HEIGHT)])
        self.observation_space = spaces.Box(low=np.zeros(self.observation_shape),
                                            high=np.full(self.observation_shape, 255),
                                            dtype=np.uint8)

        # Define an action space ranging from 0 to 5
        self.action_space = spaces.Discrete(6, )
        print(self.action_space)

        # Create a canvas to draw the game on
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR,
                              dtype=np.uint8)

        # Create the game objects in the environment
        self.player = Ship('Player', GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2, angle=0, speed=0, player=True)
        self.enemies = []
        self.missiles = []

        # Keeping track of stuff
        self.time_buffer = 0
        self.total_reward = 0

    def draw_element_on_canvas(self, element):
        if self.structure.covers(element.hit_box):
            (minx, miny, maxx, maxy) = element.hit_box.bounds
            (minx, miny, maxx, maxy) = (int(minx), int(miny), int(maxx), int(maxy))
            self.canvas[GAME_WINDOW_HEIGHT - maxy:GAME_WINDOW_HEIGHT - miny, minx:maxx] = \
                element.icon[
                element.padded_icon_h - (element.padded_icon_h - (maxy - miny)) // 2 - (maxy - miny):
                element.padded_icon_h - (element.padded_icon_h - (maxy - miny)) // 2,
                (element.padded_icon_w - (maxx - minx)) // 2:
                (element.padded_icon_w - (maxx - minx)) // 2 + (maxx - minx)
                ]

    def draw_elements_on_canvas(self):
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR,
                              dtype=np.uint8)
        self.draw_element_on_canvas(self.player)
        for enemy in self.enemies:
            self.draw_element_on_canvas(enemy)

        for missile in self.missiles:
            self.draw_element_on_canvas(missile)

        text = 'Score: ' + str(self.total_reward)
        self.canvas = cv2.putText(self.canvas, text, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1,
                                  cv2.LINE_AA)

    def reset(self):
        self.time_buffer = 0
        self.total_reward = 0

        self.player = Ship('Player', GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2, angle=0, speed=0, player=True)
        self.enemies = []
        self.missiles = []

        return cv2.resize(self.canvas, (OBSERVATION_WIDTH, OBSERVATION_HEIGHT))

    def render(self, mode='human'):
        assert mode in ['human', 'rgb_array'], 'Invalid mode, must be either "human" or "rgb_array"'
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(10)
        elif mode == "rgb_array":
            return self.canvas

    def close(self):
        cv2.destroyAllWindows()

    def step(self, action):
        done = False

        # Apply the chosen action
        assert self.action_space.contains(action), "Invalid Action"
        if action == TURN_LEFT:
            self.player.rotate(ROTATION_ANGLE)
        elif action == TURN_RIGHT:
            self.player.rotate(-ROTATION_ANGLE)
        elif action == ACCELERATE:
            self.player.accelerate()
        elif action == DECELERATE:
            self.player.decelerate()
        elif action == FIRE_MISSILE and self.player.can_fire_missile():
            missile_x = self.player.x + round(np.cos(np.radians(self.player.angle)) * MISSILE_SPEED ** 1.7)
            missile_y = self.player.y + round(np.sin(np.radians(self.player.angle)) * MISSILE_SPEED ** 1.7)
            self.missiles.append(Missile('Player-Missile', missile_x, missile_y, self.player.angle, MISSILE_SPEED))

        # Update the state of all elements in the game world and draw them on the game canvas
        self.player.move()

        if self.total_reward % SPAWN_ENEMIES_INTERVAL == 0 and self.time_buffer == 0:
            self.enemies.append(
                Ship('Enemy Ship', 50, random.randint(50, GAME_WINDOW_HEIGHT - 50), angle=0, speed=SHIP_MAX_SPEED // 2,
                     player=False))
            self.enemies.append(
                Ship('Enemy Ship', GAME_WINDOW_WIDTH - 50, random.randint(50, GAME_WINDOW_HEIGHT - 50), angle=180, speed=SHIP_MAX_SPEED // 2,
                     player=False))

        for enemy in self.enemies:
            angle_to_player = math.degrees(math.atan2(self.player.y - enemy.y, self.player.x - enemy.x))
            if angle_to_player > enemy.angle:
                enemy.rotate(min(ROTATION_ANGLE, angle_to_player - enemy.angle))
            else:
                enemy.rotate(max(-ROTATION_ANGLE, angle_to_player - enemy.angle))
            enemy.move()

            if random.randint(0, ENEMY_MISSILE_CHANCE) == ENEMY_MISSILE_CHANCE and enemy.can_fire_missile():
                missile_x = enemy.x + round(np.cos(np.radians(enemy.angle)) * MISSILE_SPEED ** 1.7)
                missile_y = enemy.y + round(np.sin(np.radians(enemy.angle)) * MISSILE_SPEED ** 1.7)
                self.missiles.append(Missile('Enemy-Missile', missile_x, missile_y, enemy.angle, MISSILE_SPEED))

        for missile in self.missiles:
            missile.move()

        self.draw_elements_on_canvas()

        # Calculate the observed reward and check if the game is over
        reward = 0
        self.time_buffer += 1
        if self.time_buffer % TIME_REWARD_THRESHOLD == 0 and self.time_buffer != 0:
            self.time_buffer = 0
            reward += TIME_REWARD

        for enemy in self.enemies:
            for other_enemy in self.enemies:
                if enemy is not other_enemy and enemy.hit_box.intersects(other_enemy.hit_box):
                    self.enemies.remove(enemy)
                    self.enemies.remove(other_enemy)
                    reward += ENEMY_CRASH_REWARD

            if not self.structure.covers(enemy.hit_box):
                self.enemies.remove(enemy)

            if self.player.hit_box.intersects(enemy.hit_box):
                done = True
                reward = LOSS_REWARD

        for missile in self.missiles:
            if missile.hit_box.intersects(self.player.hit_box):
                done = True
                reward = LOSS_REWARD

            for enemy in self.enemies:
                if missile.hit_box.intersects(enemy.hit_box):
                    reward += MISSILE_REWARD
                    self.missiles.remove(missile)
                    self.enemies.remove(enemy)

        if not self.structure.covers(self.player.hit_box):
            done = True
            reward = LOSS_REWARD

        self.total_reward += reward
        return cv2.resize(self.canvas, (OBSERVATION_WIDTH, OBSERVATION_HEIGHT)), reward, done, []
