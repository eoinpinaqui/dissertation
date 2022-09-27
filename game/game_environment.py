import gym
import game.game_object
import numpy as np
import shapely.geometry.polygon
import cv2


class GameEnvironment(gym.Env):
    __CANVAS_WIDTH = 800
    __CANVAS_HEIGHT = 800

    def __init__(self):
        super(GameEnvironment, self).__init__()

        # Define an empty list of game objects
        self.__elements = []

        # Define the canvas that elements will be drawn on
        self.__canvas_dimensions = (self.__CANVAS_WIDTH, self.__CANVAS_HEIGHT)
        self.__canvas = np.ones(self.__canvas_dimensions)
        self.__canvas_shape = shapely.geometry.polygon.Polygon([(0, 0),
                                                                (self.__CANVAS_WIDTH, 0),
                                                                (self.__CANVAS_WIDTH, self.__CANVAS_HEIGHT),
                                                                (0, self.__CANVAS_HEIGHT)])

        # Define the action and observation spaces for DRL
        self.__action_space = gym.spaces.Discrete(4)
        self.__observation_space = gym.spaces.Box(low=np.zeros(self.__canvas_dimensions),
                                                  high=np.ones(self.__canvas_dimensions),
                                                  dtype=np.float64)

    def draw_elements_on_canvas(self) -> None:
        self.__canvas = np.ones(self.__canvas_dimensions)

        for element in self.__elements:
            element_shape = element.get_shape()
            if self.__canvas_shape.covers(element_shape):
                (minx, miny, maxx, maxy) = element_shape.bounds
                (minx, miny, maxx, maxy) = (int(minx), int(miny), int(maxx), int(maxy))
                icon = element.get_icon()
                for i in range(minx, maxx):
                    for j in range(miny, maxy):
                        self.__canvas[i, j] = icon[i, j]

    def render(self, mode: str = 'human'):
        assert mode in ['human', 'rgb_array'], 'Invalid mode, must be either "human" or "rgb_array"'
        if mode == 'human':
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(1000)

        elif mode == "rgb_array":
            return self.__canvas

    def add_element(self, element: game.game_object.GameObject):
        self.__elements.append(element)