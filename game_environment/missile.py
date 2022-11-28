from .game_object import GameObject
from .game_constants import *


# Class for missiles
class Missile(GameObject):
    def __init__(self, name: str, x: int, y: int, angle: int, speed: int):
        super(Missile, self).__init__(name,
                                      f'./game_environment/sprites/missile.png',
                                      x=x,
                                      y=y,
                                      angle=angle,
                                      turning_angle=0,
                                      speed=speed,
                                      max_speed=speed,
                                      min_speed=speed,
                                      hp=MISSILE_HP)

        # Ensure the game object starts at the correct angle
        super().rotate(self.angle)
