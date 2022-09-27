import shapely.affinity
import shapely.geometry.polygon
import cv2
import numpy as np
import math


# The GameObject class defines the hit box of game objects as a 2D polygon and provides standard movement functions
class GameObject:
    def __init__(self,
                 name: str,
                 x: int = 0,
                 y: int = 0,
                 angle: int = 0,
                 velocity: int = 0,
                 icon_path: str = '',
                 points: np.array = np.zeros((3, 2))) -> None:
        self.__name = name
        self.__x = x
        self.__y = y
        self.__angle = angle
        self.__velocity = velocity
        self.__icon = cv2.imread(icon_path)
        self.__icon_height, self.__icon_width, self.__icon_channels = self.__icon.shape
        self.__shape = shapely.geometry.polygon.Polygon(points)

    def move(self) -> None:
        x_offset = np.cos(math.radians(self.__angle) * self.__velocity)
        y_offset = np.sin(math.radians(self.__angle) * self.__velocity)

        self.__x = int(np.round(self.__x + x_offset))
        self.__y = int(np.round(self.__y + y_offset))
        self.__shape = shapely.affinity.translate(self.__shape,
                                                  xoff=x_offset,
                                                  yoff=y_offset)

    def accelerate(self, upper_speed_limit: int) -> None:
        self.__velocity = min(upper_speed_limit, self.__velocity + 1)

    def decelerate(self, lower_spped_limit: int) -> None:
        self.__velocity = max(lower_spped_limit, self.__velocity - 1)

    def rotate(self, angle_of_rotation: int) -> None:
        self.__angle += angle_of_rotation
        self.__shape = shapely.affinity.rotate(self.__shape, angle_of_rotation)
        transformation_matrix = cv2.getRotationMatrix2D((self.__icon_width // 2, self.__icon_height // 2), self.__angle,
                                                        1.0)
        self.__icon = cv2.warpAffine(self.__icon, transformation_matrix, (self.__icon_width, self.__icon_height))

    # Useful getters and setters
    def get_position(self) -> tuple[int, int]:
        return self.__x, self.__y

    def get_shape(self) -> shapely.geometry.polygon.Polygon:
        return self.__shape

    def set_shape(self, points: np.array) -> None:
        self.__shape = shapely.geometry.polygon.Polygon(points)

    def get_angle(self) -> int:
        return self.__angle

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str) -> None:
        self.__name = name

    def get_icon(self):
        return self.__icon

    def get_icon_shape(self) -> tuple[int, int, int]:
        return self.__icon_height, self.__icon_width, self.__icon_channels

    def print(self) -> None:
        print(f'name: {self.__name}, x: {self.__x}, y: {self.__y}, angle: {self.__angle}, velocity: {self.__velocity}')
