from .game_object import GameObject
from .game_constants import *
import numpy as np


# Class for gunners
class Gunner(GameObject):
    def __init__(self, name: str, x: int, y: int, angle: int, speed: int, team: int):
        super(Gunner, self).__init__(name,
                                     f'./game_environment/sprites/team{team}/gunner.png',
                                     x=x,
                                     y=y,
                                     angle=angle,
                                     turning_angle=GUNNER_TURNING_ANGLE,
                                     speed=speed,
                                     max_speed=GUNNER_MAX_SPEED,
                                     min_speed=GUNNER_MIN_SPEED,
                                     hp=GUNNER_HP)

        # Some custom stuff for the gunner class
        self.missile_threshold = 0
        points = np.zeros((4, 2))
        points[0] = (self.x - (4 + self.icon_w) // 2, y - (4 + self.icon_h) // 4)
        points[1] = (self.x - (4 + self.icon_w) // 2, y + (4 + self.icon_h) // 4)
        points[2] = (self.x + (4 + self.icon_w) // 2, y + (4 + self.icon_h) // 4)
        points[3] = (self.x + (4 + self.icon_w) // 2, y - (4 + self.icon_h) // 4)
        super().set_hit_box(points)

        # Ensure the game object starts at the correct angle
        super().rotate(self.angle)

    def move(self):
        super(Gunner, self).move()
        self.missile_threshold += 1

    def fire_missile(self):
        if self.missile_threshold > GUNNER_FIRE_THRESHOLD:
            self.missile_threshold = 0
            return True
        return False
