from gym import Env, spaces
from .game_constants import GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS, BACKGROUND_COLOUR, \
    OBSERVATION_WIDTH, OBSERVATION_HEIGHT, TIME_REWARD, TIME_REWARD_THRESHOLD, CRASH_REWARD
from .ship import Ship
from shapely.geometry.polygon import Polygon
import numpy as np
import cv2


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

        # Define an action space ranging from 0 to 4
        self.action_space = spaces.Discrete(5, )

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

        text = 'Score: ' + str(self.total_reward)
        self.canvas = cv2.putText(self.canvas, text, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1,
                                  cv2.LINE_AA)

    def reset(self):
        self.time_buffer = 0
        self.total_reward = 0

        self.player = Ship('Player', GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2, angle=0, speed=0, player=True)
        self.enemies = [
            Ship('Enemy', GAME_WINDOW_WIDTH // 4, GAME_WINDOW_HEIGHT // 4, angle=0, speed=0, player=False),
            Ship('Enemy', GAME_WINDOW_WIDTH // 4, GAME_WINDOW_HEIGHT // 2, angle=0, speed=0, player=False),
            Ship('Enemy', GAME_WINDOW_WIDTH // 4, 3 * GAME_WINDOW_HEIGHT // 4, angle=0, speed=0, player=False)
        ]
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
        if action == 0:
            self.player.rotate(6)
        elif action == 1:
            self.player.rotate(-6)
        elif action == 2:
            self.player.accelerate()
        elif action == 3:
            self.player.decelerate()

        # Update the state of all elements in the game world
        self.player.move()
        self.draw_elements_on_canvas()

        # Calculate the observed reward
        reward = 0
        self.time_buffer += 1
        if self.time_buffer % TIME_REWARD_THRESHOLD == 0 and self.time_buffer != 0:
            self.time_buffer = 0
            reward += TIME_REWARD

        # Check if the game is over
        if not self.structure.covers(self.player.hit_box):
            done = True
            reward = CRASH_REWARD

        for enemy in self.enemies:
            if self.player.hit_box.intersects(enemy.hit_box):
                done = True
                reward = CRASH_REWARD

        self.total_reward += reward
        return cv2.resize(self.canvas, (OBSERVATION_WIDTH, OBSERVATION_HEIGHT)), reward, done, []
