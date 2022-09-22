import game.game_object
import cv2
import numpy as np


class Player(game.game_object.GameObject):
    __MIN_VELOCITY = 0
    __MAX_VELOCITY = 10

    def __init__(self, name: str, x: int, y: int, angle: int, velocity: int = 0) -> None:
        super(Player, self).__init__(name, x, y, angle)
        self.__velocity = velocity
        self.__icon = cv2.imread('./game/sprites/player.png')
        self.__icon_height, self.__icon_width, self.__icon_channels = self.__icon.shape

        p = np.zeros((4, 2))
        p[0] = (x - self.__icon_width / 4, y - self.__icon_height / 2)
        p[1] = (x + self.__icon_width / 4, y - self.__icon_height / 2)
        p[2] = (x + self.__icon_width / 4, y + self.__icon_height / 2)
        p[3] = (x - self.__icon_width / 4, y + self.__icon_height / 2)
        super(Player, self).set_shape(p)

    def accelerate(self) -> None:
        self.__velocity = min(self.__MAX_VELOCITY, self.__velocity + 1)

    def decelerate(self) -> None:
        self.__velocity = max(self.__MIN_VELOCITY, self.__velocity - 1)

    def move(self) -> None:
        super(Player, self).move(self.__velocity)

    def rotate(self, angle_of_rotation) -> None:
        super(Player, self).rotate(angle_of_rotation)
        transformation_matrix = cv2.getRotationMatrix2D((self.__icon_width // 2, self.__icon_height // 2),
                                                        super(Player, self).get_angle(),
                                                        1.0)
        self.__icon = cv2.warpAffine(self.__icon, transformation_matrix, (self.__icon_width, self.__icon_height))

    def print(self) -> None:
        super(Player, self).print()
        print(f'velocity: {self.__velocity}')
