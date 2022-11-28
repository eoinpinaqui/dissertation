# Constants for the game world
GAME_WINDOW_WIDTH = 1500
GAME_WINDOW_HEIGHT = 1500
GAME_WINDOW_CHANNELS = 3
BACKGROUND_COLOUR = [255, 177, 105]

# Constants for gunners
GUNNER_MAX_SPEED = 6
GUNNER_MIN_SPEED = -2
GUNNER_TURNING_ANGLE = 3
GUNNER_FIRE_THRESHOLD = 250
GUNNER_HP = 2
GUNNER_COST = 50

# Constants for scouts
SCOUT_MAX_SPEED = 12
SCOUT_MIN_SPEED = -4
SCOUT_TURNING_ANGLE = 6
SCOUT_FIRE_THRESHOLD = 1000
SCOUT_HP = 1
SCOUT_COST = 50

# Constants for tanks
TANK_MAX_SPEED = 3
TANK_MIN_SPEED = -1
TANK_TURNING_ANGLE = 3
TANK_FIRE_THRESHOLD = 500
TANK_HP = 4
TANK_COST = 50

# Constants for teams
TEAM_PASSIVE_THRESHOLD = 40
TEAM_GOLD_START = 100
TEAM_GOLD_DELTA = 25
TEAM_AMMO_START = 5
TEAM_AMMO_DELTA = 1
TEAM_COLOURS = {
    1: [255, 0, 0],
    2: [0, 0, 255],
    3: [0, 255, 0],
    4: [0, 255, 255]
}
TEAM_BASE_COORDS = {
    1: [0, 0],
    2: [GAME_WINDOW_WIDTH, 0],
    3: [GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT],
    4: [0, GAME_WINDOW_HEIGHT]
}
BASE_MARGIN = 50

# Constants for missiles
MISSILE_SPEED = 15
MISSILE_MAX_SPEED = 15
MISSILE_MIN_SPEED = 15
MISSILE_COST = 1
MISSILE_HP = 1

# Constants for game actions
DO_NOTHING = 0
ACCELERATE = 1
DECELERATE = 2
TURN_LEFT = 3
TURN_RIGHT = 4
FIRE_MISSILE = 5
CHANGE_SHIP = 6
SPAWN_GUNNER = 7
SPAWN_SCOUT = 8
SPAWN_TANK = 9

