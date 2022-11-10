from gym import Env, spaces
from .game_constants import GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS, BACKGROUND_COLOUR, \
    OBSERVATION_WIDTH, OBSERVATION_HEIGHT
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
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR, dtype=np.uint8)

        # Create the game objects in the environment
        self.player = Ship('Player', GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2, angle=0, speed=0, player=True)
        self.enemies = []
        self.missiles = []
        self.time = 0
        self.time_buffer = 0

    def draw_element_on_canvas(self, element):
        if self.structure.covers(element.hit_box):
            left_gap = element.x - element.padded_icon_w // 2
            right_gap = element.x + element.padded_icon_w // 2
            top_gap = element.y - element.padded_icon_h // 2
            bottom_gap = element.y + element.padded_icon_h // 2

            start_canvas_x = max(0, left_gap)
            end_canvas_x = min(GAME_WINDOW_WIDTH, right_gap)
            start_canvas_y = max(0, top_gap)
            end_canvas_y = min(GAME_WINDOW_HEIGHT, bottom_gap)

            start_icon_x = 0 if left_gap > 0 else abs(left_gap)
            end_icon_x = element.padded_icon_w if right_gap < GAME_WINDOW_WIDTH else element.padded_icon_w - (right_gap - GAME_WINDOW_WIDTH)
            start_icon_y = 0 if top_gap > 0 else abs(top_gap)
            end_icon_y = element.padded_icon_h if top_gap < GAME_WINDOW_HEIGHT else element.padded_icon_h - (top_gap - GAME_WINDOW_HEIGHT)

            self.canvas[start_canvas_y:end_canvas_y, start_canvas_x:end_canvas_x] = element.icon[start_icon_y:end_icon_y, start_icon_x: end_icon_x]

    def draw_elements_on_canvas(self):
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR, dtype=np.uint8)
        self.draw_element_on_canvas(self.player)

    def reset(self):
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

        assert self.action_space.contains(action), "Invalid Action"

        if action == 0:
            self.player.rotate(6)
        elif action == 1:
            self.player.rotate(-6)
        elif action == 2:
            self.player.accelerate()
        elif action == 3:
            self.player.decelerate()

        self.player.move()

        self.draw_elements_on_canvas()

        if not self.structure.covers(self.player.hit_box):
            done = True

        return cv2.resize(self.canvas, (OBSERVATION_WIDTH, OBSERVATION_HEIGHT)), 1, done, []
