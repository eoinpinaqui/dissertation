from .game_object import GameObject
from .game_constants import *
import numpy as np


# Class for coins
class Coin(GameObject):
    def __init__(self, name: str, x: int, y: int):
        super(Coin, self).__init__(name,
                                   f'./game_environment/sprites/coin.png',
                                   x=x,
                                   y=y,
                                   angle=0,
                                   turning_angle=0,
                                   speed=0,
                                   max_speed=0,
                                   min_speed=0,
                                   hp=1)

        # Some custom stuff for the coin class
        self.time = 0
        points = np.zeros((4, 2))
        points[0] = (self.x - (4 + self.icon_w) // 4, y - (4 + self.icon_h) // 4)
        points[1] = (self.x - (4 + self.icon_w) // 4, y + (4 + self.icon_h) // 4)
        points[2] = (self.x + (4 + self.icon_w) // 4, y + (4 + self.icon_h) // 4)
        points[3] = (self.x + (4 + self.icon_w) // 4, y - (4 + self.icon_h) // 4)
        super().set_hit_box(points)

        # Ensure the game object starts at the correct angle
        super().rotate(self.angle)

    def step(self):
        self.time += 1

    def timeout(self):
        return self.time >= COIN_TIMEOUT
