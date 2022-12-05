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
                    if x < GAME_WINDOW_WIDTH:
                        self.canvas[y, x] = border

            for x in [minx, maxx]:
                for y in range(max(GAME_WINDOW_HEIGHT - maxy, 0),
                               min(GAME_WINDOW_HEIGHT - miny, GAME_WINDOW_HEIGHT - 1)):
                    if x < GAME_WINDOW_WIDTH:
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
                self.draw_element_on_canvas(missile, BACKGROUND_COLOUR)

        # Draw the bases


        # Draw the game stats
        blue_gold = f'Gold: {self.teams[0].gold}'
        red_gold = f'Gold: {self.teams[1].gold}'
        green_gold = f'Gold: {self.teams[2].gold}'
        yellow_gold = f'Gold: {self.teams[3].gold}'
        blue_ammo = f'Ammo: {self.teams[0].ammo}'
        red_ammo = f'Ammo: {self.teams[1].ammo}'
        green_ammo = f'Ammo: {self.teams[2].ammo}'
        yellow_ammo = f'Ammo: {self.teams[3].ammo}'
        self.canvas = cv2.putText(self.canvas, blue_gold, (0, GAME_WINDOW_HEIGHT - 5),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, blue_ammo, (0, GAME_WINDOW_HEIGHT - 20),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, red_gold, (GAME_WINDOW_WIDTH - BASE_MARGIN * 2, GAME_WINDOW_HEIGHT - 5),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, red_ammo, (GAME_WINDOW_WIDTH - BASE_MARGIN * 2, GAME_WINDOW_HEIGHT - 20),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, green_gold, (GAME_WINDOW_WIDTH - BASE_MARGIN * 2, 15),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, green_ammo, (GAME_WINDOW_WIDTH - BASE_MARGIN * 2, 30),
                                  cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, yellow_gold, (0, 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1,
                                  cv2.LINE_AA)
        self.canvas = cv2.putText(self.canvas, yellow_ammo, (0, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 0), 1,
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

            # Check for missile collisions
            for m, missile in enumerate(self.teams[team].missiles):
                if not self.structure.covers(missile.hit_box):
                    self.teams[team].missiles.remove(missile)
                    continue

                missile_removed = False
                for i, fleet in enumerate(self.teams):
                    if missile_removed:
                        break
                    for j, ship in enumerate(fleet.ships):
                        if missile_removed:
                            break
                        if missile.hit_box.intersects(ship.hit_box):
                            missile_removed = True
                            self.teams[team].missiles.remove(missile)
                            self.teams[i].ships[j].hp -= 1
                        if ship.hp < 1:
                            self.teams[i].ships.remove(self.teams[i].ships[j])
                            if self.teams[i].current_ship >= j:
                                self.teams[i].current_ship -= 1

            # Check for ship collisions
            for s, ship in enumerate(self.teams[team].ships):
                if not self.structure.covers(ship.hit_box):
                    self.teams[team].ships.remove(ship)
                    if self.teams[team].current_ship >= s:
                        self.teams[team].current_ship -= 1
                    continue

                ship_removed = False
                for i, fleet in enumerate(self.teams):
                    if ship_removed:
                        break
                    for j, other_ship in enumerate(fleet.ships):
                        if ship_removed:
                            break
                        if ship != other_ship and ship.hit_box.intersects(other_ship.hit_box):
                            ship_removed = True
                            self.teams[team].ships.remove(ship)
                            self.teams[i].ships.remove(other_ship)
                            if self.teams[team].current_ship >= s:
                                self.teams[team].current_ship -= 1
                            if self.teams[i].current_ship >= j:
                                self.teams[j].current_ship -= 1

        self.draw_elements_on_canvas()

        # Calculate the observed reward and check if the game is over
        reward = 0

        return self.canvas, reward, done, []
