import numpy as np
from shapely.geometry.polygon import Polygon
from shapely import affinity
import cv2
from .game_constants import BACKGROUND_COLOUR


# Base class for all objects that exist in the game world
class GameObject(object):
    def __init__(self,
                 name: str,
                 icon_path: str,
                 x: int = 0,
                 y: int = 0,
                 angle: int = 0,
                 turning_angle: int = 0,
                 speed: int = 0,
                 min_speed: int = 0,
                 max_speed: int = 0,
                 hp: int = 1,
                 hit_box: np.array = None):
        # Copy over all the data
        if hit_box is None:
            hit_box = [(0, 0)]
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle
        self.turning_angle = turning_angle
        self.speed = speed
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.hp = hp
        self.hit_box = hit_box

        # Read in the icon
        self.icon = cv2.imread(icon_path)
        self.icon = cv2.resize(self.icon, (self.icon.shape[0] * 2, self.icon.shape[1] * 2))
        (self.icon_w, self.icon_h, self.icon_c) = self.icon.shape

        # Create a padding around the icon so that the rotations don't clip
        self.padded_icon_w = self.icon_w * 2
        self.padded_icon_h = self.icon_h * 2
        self.padded_icon = np.full((self.padded_icon_w, self.padded_icon_h, self.icon_c), BACKGROUND_COLOUR,
                                   dtype=np.uint8)
        w_margin = (self.padded_icon_w - self.icon_w) // 2
        h_margin = (self.padded_icon_h - self.icon_h) // 2
        self.padded_icon[w_margin:w_margin + self.icon_w, h_margin:h_margin + self.icon_h] = self.icon
        self.icon = self.padded_icon

    def set_hit_box(self, points):
        self.hit_box = Polygon(points)

    def move(self):
        x_off = round(np.cos(np.radians(self.angle)) * self.speed)
        y_off = round(np.sin(np.radians(self.angle)) * self.speed)
        self.x += x_off
        self.y += y_off
        self.hit_box = affinity.translate(self.hit_box, xoff=x_off, yoff=y_off)

    def rotate_left(self):
        self.rotate(self.turning_angle)

    def rotate_right(self):
        self.rotate(-self.turning_angle)

    def rotate(self, degree):
        self.angle += degree
        self.hit_box = affinity.rotate(self.hit_box, degree, 'center')
        m = cv2.getRotationMatrix2D((self.padded_icon_w // 2, self.padded_icon_h // 2), self.angle, 1)
        self.icon = cv2.warpAffine(self.padded_icon, m, (self.padded_icon_w, self.padded_icon_h),
                                   borderValue=BACKGROUND_COLOUR)

    def accelerate(self):
        self.speed = min(self.speed + 1, self.max_speed)

    def decelerate(self):
        self.speed = max(self.speed - 1, self.min_speed)

    def decrease_hp(self):
        self.hp -= 1
