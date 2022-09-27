import game_environment.game_object
import numpy as np


class Player(game_environment.game_object.GameObject):
    __MIN_VELOCITY = 0
    __MAX_VELOCITY = 10
    __ICON_PATH = './game/sprites/player.png'

    def __init__(self, name: str, x: int = 0, y: int = 0, angle: int = 0, velocity: int = 0) -> None:
        super(Player, self).__init__(name, x, y, angle, velocity, self.__ICON_PATH)

        icon_height, icon_width, icon_channels = super(Player, self).get_icon_shape()

        p = np.zeros((4, 2))
        p[0] = (x - icon_width / 4, y - icon_height / 2)
        p[1] = (x + icon_width / 4, y - icon_height / 2)
        p[2] = (x + icon_width / 4, y + icon_height / 2)
        p[3] = (x - icon_width / 4, y + icon_height / 2)
        super(Player, self).set_shape(p)

    def accelerate(self):
        super(Player, self).accelerate(self.__MAX_VELOCITY)

    def decelerate(self):
        super(Player, self).decelerate(self.__MIN_VELOCITY)
