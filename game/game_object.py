import shapely.affinity
import shapely.geometry.polygon
import numpy as np
import math


# The GameObject class defines the hit box of game objects as a 2D polygon and provides standard movement functions
class GameObject:
    def __init__(self, name: str, x: int = 0, y: int = 0, angle: int = 0, points: np.array = np.zeros((3, 2))) -> None:
        self.__name = name
        self.__x = x
        self.__y = y
        self.__angle = angle
        self.__shape = shapely.geometry.polygon.Polygon(points)

    def move(self, velocity: float) -> None:
        x_offset = np.cos(math.radians(self.__angle) * velocity)
        y_offset = np.sin(math.radians(self.__angle) * velocity)

        self.__x = int(np.round(self.__x + x_offset))
        self.__y = int(np.round(self.__y + y_offset))
        self.__shape = shapely.affinity.translate(self.__shape,
                                                  xoff=x_offset,
                                                  yoff=y_offset)

    def rotate(self, angle_of_rotation: int) -> None:
        self.__angle += angle_of_rotation
        self.__shape = shapely.affinity.rotate(self.__shape, angle_of_rotation)

    # Useful getters and setters
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

    def print(self) -> None:
        print(f'name: {self.__name}, x: {self.__x}, y: {self.__y}, angle: {self.__angle}')
