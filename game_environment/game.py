from gym import Env, spaces
from .game_constants import *
from .team import Team
from shapely.geometry.polygon import Polygon
import numpy as np
import cv2


class Game(Env):
    def __init__(self):
        super().__init__()

        # Define the observation space
        self.observation_shape = (GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS)
        self.structure = Polygon(
            [(0, 0), (GAME_WINDOW_WIDTH, 0), (GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT), (0, GAME_WINDOW_HEIGHT)])
        self.observation_space = spaces.Box(low=np.zeros(self.observation_shape),
                                            high=np.full(self.observation_shape, 255),
                                            dtype=np.uint8)

        # Define an action space ranging from 0 to 6
        self.action_space = spaces.Discrete(10, )
        print(self.action_space)

        # Create a canvas to draw the game on
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR,
                              dtype=np.uint8)

        self.teams = []
        for i in range(1, 5):
            self.teams.append(Team(i))

    def draw_element_on_canvas(self, element, border):
        if self.structure.covers(element.hit_box):
            (minx, miny, maxx, maxy) = element.hit_box.bounds
            (minx, miny, maxx, maxy) = (int(minx), int(miny), int(maxx), int(maxy))
            self.canvas[GAME_WINDOW_HEIGHT - maxy:GAME_WINDOW_HEIGHT - miny, minx:maxx] = \
                element.icon[
                element.padded_icon_h - (element.padded_icon_h - (maxy - miny)) // 2 - (maxy - miny):
                element.padded_icon_h - (element.padded_icon_h - (maxy - miny)) // 2,
                (element.padded_icon_w - (maxx - minx)) // 2:
                (element.padded_icon_w - (maxx - minx)) // 2 + (maxx - minx)
                ]

            for y in [max(GAME_WINDOW_HEIGHT - maxy, 0),
                      min(GAME_WINDOW_HEIGHT - miny, GAME_WINDOW_HEIGHT - 1)]:
                for x in range(minx, maxx):
                    self.canvas[y, x] = border

            for x in [minx, maxx]:
                for y in range(max(GAME_WINDOW_HEIGHT - maxy, 0),
                               min(GAME_WINDOW_HEIGHT - miny, GAME_WINDOW_HEIGHT - 1)):
                    self.canvas[y, x] = border

    def draw_elements_on_canvas(self):
        self.canvas = np.full((GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, GAME_WINDOW_CHANNELS), BACKGROUND_COLOUR,
                              dtype=np.uint8)
        for team in self.teams:
            for idx, ship in enumerate(team.ships):
                if idx == team.current_ship:
                    border = team.color
                else:
                    border = BACKGROUND_COLOUR
                self.draw_element_on_canvas(ship, border)

            for missile in team.missiles:
                self.draw_element_on_canvas(missile)

        text = f'Gold: {self.teams[0].gold} Current: {self.teams[0].current_ship}'
        self.canvas = cv2.putText(self.canvas, text, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1,
                                  cv2.LINE_AA)

    def reset(self):
        self.teams = []
        for i in range(1, 5):
            self.teams.append(Team(i))
        return self.canvas

    def render(self, mode='human'):
        assert mode in ['human', 'rgb_array'], 'Invalid mode, must be either "human" or "rgb_array"'
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(10)
        elif mode == "rgb_array":
            return self.canvas

    def close(self):
        cv2.destroyAllWindows()

    def step(self, actions):
        done = False

        for team, action in enumerate(actions):
            # Move all elements in a team
            self.teams[team].step()

            # Apply the chosen action for a team
            assert self.action_space.contains(action), f'Invalid Action for team {team}'
            if action == ACCELERATE:
                self.teams[team].accelerate()
            elif action == DECELERATE:
                self.teams[team].decelerate()
            elif action == TURN_LEFT:
                self.teams[team].turn_left()
            elif action == TURN_RIGHT:
                self.teams[team].turn_right()
            elif action == FIRE_MISSILE:
                self.teams[team].fire_missile()
            elif action == CHANGE_SHIP:
                self.teams[team].change_ship()
            elif action == SPAWN_GUNNER:
                self.teams[team].spawn_gunner()
            elif action == SPAWN_SCOUT:
                self.teams[team].spawn_scout()
            elif action == SPAWN_TANK:
                self.teams[team].spawn_tank()

            for idx, ship in enumerate(self.teams[team].ships):
                if not self.structure.covers(ship.hit_box):
                    self.teams[team].ships.remove(ship)
                    if idx > self.teams[team].current_ship:
                        self.teams[team].current_ship -= 1

        self.draw_elements_on_canvas()

        # Calculate the observed reward and check if the game is over
        reward = 0

        return self.canvas, reward, done, []
