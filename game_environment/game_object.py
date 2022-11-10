import numpy as np
from shapely.geometry.polygon import Polygon
from shapely import affinity
from .game_constants import *


# Base class for all objects that exist in the game world
class GameObject(object):
    def __init__(self, name: str, x: int = 0, y: int = 0, angle: int = 0, speed: int = 0, hit_box: np.array = None,
                 max_speed: int = SHIP_MAX_SPEED, min_speed: int = SHIP_MIN_SPEED):
        if hit_box is None:
            hit_box = [(0, 0)]
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.hit_box = hit_box
        self.max_speed = max_speed
        self.min_speed = min_speed

    def set_hit_box(self, points):
        self.hit_box = Polygon(points)

    def move(self):
        x_off = round(np.sin(np.radians(self.angle)) * self.speed)
        y_off = round(np.cos(np.radians(self.angle)) * self.speed)
        self.x += x_off
        self.y += y_off
        self.hit_box = affinity.translate(self.hit_box, xoff=x_off, yoff=y_off)

    def rotate(self, degree):
        self.angle += degree
        self.hit_box = affinity.rotate(self.hit_box, degree, 'center')

    def accelerate(self):
        self.speed = min(self.speed + 1, self.max_speed)

    def decelerate(self):
        self.speed = max(self.speed - 1, self.min_speed)
