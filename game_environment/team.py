from .game_constants import *
from .gunner import Gunner
from .scout import Scout
from .tank import Tank
from .missile import Missile
import numpy as np


class Team:
    def __init__(self, team_number):
        self.team_number = team_number
        self.ships = []
        self.missiles = []
        self.current_ship = 0
        self.gold = TEAM_GOLD_START
        self.ammo = 0
        self.delta = 0
        self.color = TEAM_COLOURS[self.team_number]
        (self.x, self.y) = TEAM_BASE_COORDS[self.team_number]
        self.ship_start_x = BASE_MARGIN * 2 if self.x < BASE_MARGIN else GAME_WINDOW_WIDTH - BASE_MARGIN * 2
        self.ship_start_y = BASE_MARGIN * 2 if self.y < BASE_MARGIN else GAME_WINDOW_HEIGHT - BASE_MARGIN * 2


    def step(self):
        # Check if passive gold has been earned
        self.delta += 1
        if self.delta > TEAM_PASSIVE_THRESHOLD:
            self.add_gold(TEAM_GOLD_DELTA)
            self.add_ammo(TEAM_AMMO_DELTA)
            self.delta = 0

        if self.current_ship >= len(self.ships):
            self.change_ship()

        # Move all the ships
        for ship in self.ships:
            ship.move()

        # Move all the missiles
        for missile in self.missiles:
            missile.move()

    def add_gold(self, gold: int):
        self.gold += gold

    def add_ammo(self, ammo: int):
        self.ammo += ammo

    def accelerate(self):
        if len(self.ships) < 1:
            return
        self.ships[self.current_ship].accelerate()

    def decelerate(self):
        if len(self.ships) < 1:
            return
        self.ships[self.current_ship].decelerate()

    def turn_left(self):
        if len(self.ships) < 1:
            return
        self.ships[self.current_ship].rotate_left()

    def turn_right(self):
        if len(self.ships) < 1:
            return
        self.ships[self.current_ship].rotate_right()

    def fire_missile(self):
        if self.ammo < MISSILE_COST or len(self.ships) < 1:
            return

        if self.ships[self.current_ship].fire_missile():
            self.ammo -= MISSILE_COST
            current_ship = self.ships[self.current_ship]
            missile_x = current_ship.x + round(np.cos(np.radians(current_ship.angle)) * MISSILE_SPEED ** 1.7)
            missile_y = current_ship.y + round(np.sin(np.radians(current_ship.angle)) * MISSILE_SPEED ** 1.7)
            self.missiles.append(
                Missile(f'Team {self.team_number} Missile', missile_x, missile_y, current_ship.angle, MISSILE_SPEED))

    def change_ship(self):
        self.current_ship += 1
        if self.current_ship >= len(self.ships):
            self.current_ship = 0

    def spawn_gunner(self):
        if self.gold > GUNNER_COST:
            self.gold -= GUNNER_COST
            self.ships.append(Gunner(f'Team {self.team_number} Gunner', self.ship_start_x, self.ship_start_y, 0, 0, self.team_number))

    def spawn_scout(self):
        if self.gold > SCOUT_COST:
            self.gold -= SCOUT_COST
            self.ships.append(Scout(f'Team {self.team_number} Scout', self.ship_start_x, self.ship_start_y, 0, 0, self.team_number))

    def spawn_tank(self):
        if self.gold > TANK_COST:
            self.gold -= TANK_COST
            self.ships.append(Tank(f'Team {self.team_number} Tank', self.ship_start_x, self.ship_start_y, 0, 0, self.team_number))
