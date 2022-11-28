from .game_object import GameObject
from .game_constants import *
import numpy as np


# Class for scouts
class Tank(GameObject):
    def __init__(self, name: str, x: int, y: int, angle: int, speed: int, team: int):
        super(Tank, self).__init__(name,
                                   f'./game_environment/sprites/team{team}/tank.png',
                                   x=x,
                                   y=y,
                                   angle=angle,
                                   turning_angle=TANK_TURNING_ANGLE,
                                   speed=speed,
                                   max_speed=TANK_MAX_SPEED,
                                   min_speed=TANK_MIN_SPEED,
                                   hp=TANK_HP)

        # Some custom stuff for the tank class
        self.missile_threshold = 0
        points = np.zeros((4, 2))
        points[0] = (self.x - (4 + self.icon_w) // 2, y - (4 + self.icon_h) // 3)
        points[1] = (self.x - (4 + self.icon_w) // 2, y + (4 + self.icon_h) // 3)
        points[2] = (self.x + (4 + self.icon_w) // 2, y + (4 + self.icon_h) // 3)
        points[3] = (self.x + (4 + self.icon_w) // 2, y - (4 + self.icon_h) // 3)
        super().set_hit_box(points)

        # Ensure the game object starts at the correct angle
        super().rotate(self.angle)

    def move(self):
        super(Tank, self).move()
        self.missile_threshold += 1

    def fire_missile(self):
        if self.missile_threshold > TANK_FIRE_THRESHOLD:
            self.missile_threshold = 0
            return True
        return False
