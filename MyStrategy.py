import numpy as np
import math

from collections import deque

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.TerrainType import TerrainType
from model.VehicleType import VehicleType
from model.VehicleUpdate import VehicleUpdate
from model.WeatherType import WeatherType
from model.World import World


""" PARAMS """
DEBUG = True

BOMBER_GROUP = 9
SANDWICH_GROUP = 1

FIGHTER_GROUP = 3
ARRV_GROUP = 4
HELICOPTER_GROUP = 5
IFV_GROUP = 6
TANK_GROUP = 7

ACTIONS = {
    0: 'NONE',
    1: 'CLEAR_AND_SELECT',
    2: 'ADD_TO_SELECTION',
    3: 'DESELECT',
    4: 'ASSIGN',
    5: 'DISMISS',
    6: 'DISBAND',
    7: 'MOVE',
    8: 'ROTATE',
    9: 'SCALE',
    10: 'SETUP_VEHICLE_PRODUCTION',
    11: 'TACTICAL_NUCLEAR_STRIKE'
}


class Timer:

    def __init__(self):
        pass


class FighterHarass:

    def __init(self):
        pass


class MainBot:
    def __init__(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self.state = ''

        self.terrain = world.terrain_by_cell_x_y
        self.weather = world.weather_by_cell_x_y
        self.orders = deque(maxlen=5000)
        self.current_order_wait = 0
        self.my_center = []
        self.enemy_center = []
        self.my_vehicles = {}
        self.my_initial_vehicles = {}
        self.enemy_initial_vehicles = {}
        self.enemy_vehicles = {}
        self.fighters, self.arrv, self.helicopters, self.ifv, self.tank = {}, {}, {}, {}, {}

        self._init_variables()

        self.whirlwind_packed = False
        self.nuclear_defence_active = 0


class MyStrategy:
    my_bot = None
    commands_executed = 0

    def game_init(self, world, game, move, me):
        self.my_bot = TShirtBot(world, game, move, me)

    def move(self, me: Player, world: World, game: Game, move: Move):
        if world.tick_index == 0:
            self.game_init(world=world, game=game, move=move, me=me)

        self.my_bot.init_tick(world, game, move, me)
        bot_answer = self.my_bot.make_decision()

        if bot_answer:
            self.commands_executed += 1
            if DEBUG:
                print('[EXECUTE: T%s: EXE:%s STATE:%s] %s %s %s' % (
                    world.tick_index, self.commands_executed, self.my_bot.state, ACTIONS[bot_answer.action],
                    bot_answer.group, bot_answer.vehicle_id))
            move.action = bot_answer.action
            move.right = bot_answer.right
            move.bottom = bot_answer.bottom
            move.left = bot_answer.left
            move.top = bot_answer.top
            move.x = bot_answer.x
            move.y = bot_answer.y
            move.factor = bot_answer.factor
            move.max_speed = bot_answer.max_speed
            move.angle = bot_answer.angle
            move.vehicle_id = bot_answer.vehicle_id
            move.group = bot_answer.group
            move.vehicle_type = bot_answer.vehicle_type
        else:
            move.action = None

