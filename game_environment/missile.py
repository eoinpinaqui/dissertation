from .game_object import GameObject
from .game_constants import *
import numpy as np


# Class for missiles
class Missile(GameObject):
    def __init__(self, name: str, x: int, y: int, angle: int, speed: int):
        super(Missile, self).__init__(name,
                                      f'./game_environment/sprites/missile.png',
                                      x=x,
                                      y=y,
                                      angle=angle,
                                      turning_angle=1,
                                      speed=speed,
                                      max_speed=speed,
                                      min_speed=speed,
                                      hp=MISSILE_HP)

        # Ensure the game object starts at the correct angle
        points = np.zeros((4, 2))
        points[0] = (self.x - 6, y - 4)
        points[1] = (self.x - 6, y + 4)
        points[2] = (self.x + 6, y + 4)
        points[3] = (self.x + 6, y - 4)
        super().set_hit_box(points)
        super().rotate(self.angle)
