from gym import Env, spaces
from .game_constants import *
from .team import Team
from .coin import Coin
from .ammo import Ammo
from shapely.geometry.polygon import Polygon
import numpy as np
import cv2
from random import randint


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

        self.power_ups = []

    def draw_base(self, team):
        (minx, miny, maxx, maxy) = team.hit_box.bounds
        (minx, miny, maxx, maxy) = (int(minx), int(miny), int(maxx), int(maxy))
        self.canvas[GAME_WINDOW_HEIGHT - maxy:GAME_WINDOW_HEIGHT - miny, minx:maxx] = team.color

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

        # Draw the collectibles
        for collectible in self.power_ups:
            self.draw_element_on_canvas(collectible, BACKGROUND_COLOUR)

        # Draw the teams
        for team in self.teams:
            if team.dead():
                continue
            for idx, ship in enumerate(team.ships):
                if idx == team.current_ship:
                    border = team.color
                else:
                    border = BACKGROUND_COLOUR
                self.draw_element_on_canvas(ship, border)

            for missile in team.missiles:
                self.draw_element_on_canvas(missile, BACKGROUND_COLOUR)

        # Draw the bases
        for team in self.teams:
            if team.dead():
                continue
            self.draw_base(team)

        # Draw the game stats
        for team in self.teams:
            if team.dead():
                continue
            gold = f'Gold: {team.gold}'
            ammo = f'Ammo: {team.ammo}'
            hp = f'HP: {team.hp}'
            self.canvas = cv2.putText(self.canvas, gold,
                                      (team.x - BASE_MARGIN // 3, GAME_WINDOW_HEIGHT - team.y - BASE_MARGIN // 4),
                                      cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            self.canvas = cv2.putText(self.canvas, ammo, (team.x - BASE_MARGIN // 3, GAME_WINDOW_HEIGHT - team.y),
                                      cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            self.canvas = cv2.putText(self.canvas, hp,
                                      (team.x - BASE_MARGIN // 3, GAME_WINDOW_HEIGHT - team.y + BASE_MARGIN // 4),
                                      cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    def reset(self):
        self.teams = []
        self.power_ups = []
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
        rewards = [0, 0, 0, 0]

        # Step all the collectibles
        for collectible in self.power_ups:
            collectible.step()
            if collectible.name == COIN_NAME and collectible.time >= COIN_TIMEOUT:
                self.power_ups.remove(collectible)
            elif collectible.name == AMMO_NAME and collectible.time >= AMMO_TIMEOUT:
                self.power_ups.remove(collectible)

        # Step all the fleets
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
                for b, base in enumerate(self.teams):
                    if missile.hit_box.intersects(base.hit_box):
                        missile_removed = True
                        self.teams[team].missiles.remove(missile)
                        self.teams[b].hp -= 1
                        if self.teams[b].hp == 0:
                            for t, other_team in enumerate(self.teams):
                                rewards[t] = 100
                                if other_team.dead():
                                    rewards[t] = 0
                            rewards[b] = -150

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

                for collectible in self.power_ups:
                    if ship.hit_box.intersects(collectible.hit_box):
                        self.power_ups.remove(collectible)
                        if collectible.name == COIN_NAME:
                            self.teams[team].gold += COIN_GOLD
                        if collectible.name == AMMO_NAME:
                            self.teams[team].ammo += AMMO_AMOUNT

                ship_removed = False
                for b, base in enumerate(self.teams):
                    if ship.hit_box.intersects(base.hit_box):
                        ship_removed = True
                        self.teams[team].ships.remove(ship)
                        self.teams[b].hp -= 1
                        if self.teams[team].current_ship >= s:
                            self.teams[team].current_ship -= 1
                        if self.teams[b].hp == 0:
                            for t, other_team in enumerate(self.teams):
                                rewards[t] = 100
                                if other_team.dead():
                                    rewards[t] = 0
                            rewards[b] = -150

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

        # Maybe spawn a collectible
        power_up = randint(0, 200)
        if power_up < 1:
            self.power_ups.append(Coin(COIN_NAME, randint(COIN_X_MIN, COIN_X_MAX), randint(COIN_Y_MIN, COIN_Y_MAX)))
        elif power_up < 2:
            self.power_ups.append(Ammo(AMMO_NAME, randint(AMMO_X_MIN, AMMO_X_MAX), randint(AMMO_Y_MIN, AMMO_Y_MAX)))

        num_dead_teams = 0
        for t, team in enumerate(self.teams):
            if team.hp <= 0:
                self.teams[t].ships = []
                self.teams[t].missiles = []
                num_dead_teams += 1

        # Draw the game
        self.draw_elements_on_canvas()

        return self.canvas, rewards, num_dead_teams >= 3, []
