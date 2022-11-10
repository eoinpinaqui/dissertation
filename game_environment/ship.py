from .game_object import GameObject
from .game_constants import BACKGROUND_COLOUR
import cv2
import numpy as np


# Class for ships
class Ship(GameObject):
    def __init__(self, name: str, x: int, y: int, angle: int, speed: int, player: bool):
        super(Ship, self).__init__(name, x=x, y=y, speed=speed)

        # Read in the appropriate icon
        icon_to_read = './game_environment/sprites/player.png' if player else './game_environment/sprites/player.png'
        temp_icon = cv2.imread(icon_to_read)
        self.icon = cv2.resize(temp_icon, (temp_icon.shape[0] * 2, temp_icon.shape[1] * 2))
        (self.icon_w, self.icon_h, self.icon_c) = self.icon.shape

        # Create a padding around the icon so that rotations don't clip
        self.padded_icon_w = self.icon_w * 2
        self.padded_icon_h = self.icon_h * 2
        self.padded_icon = np.full((self.padded_icon_w, self.padded_icon_h, self.icon_c), BACKGROUND_COLOUR, dtype=np.uint8)
        w_margin = (self.padded_icon_w - self.icon_w) // 2
        h_margin = (self.padded_icon_h - self.icon_h) // 2
        self.padded_icon[w_margin:w_margin + self.icon_w, h_margin:h_margin + self.icon_h] = self.icon
        self.icon = self.padded_icon

        # Define the hit box of the ship
        points = np.zeros((5, 2))
        points[0] = (self.x + self.icon_w, y + self.icon_h // 2)
        points[1] = (self.x + self.icon_w // 4, y - self.icon_h // 4)
        points[2] = (self.x + self.icon_w // 4, y + self.icon_h // 2)
        points[3] = (self.x - self.icon_w // 4, y + self.icon_h // 2)
        points[4] = (self.x - self.icon_w // 4, y - self.icon_h // 4)
        super().set_hit_box(points)

        # Rotate the ship
        self.rotate(angle)

    def rotate(self, degree):
        super().rotate(degree)
        m = cv2.getRotationMatrix2D((self.padded_icon_w // 2, self.padded_icon_h // 2), self.angle, 1)
        self.icon = cv2.warpAffine(self.padded_icon, m, (self.padded_icon_w, self.padded_icon_h),
                                   borderValue=BACKGROUND_COLOUR)
