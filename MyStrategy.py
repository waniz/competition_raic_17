import copy
import numpy as np
from collections import deque

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.PlayerContext import PlayerContext
from model.TerrainType import TerrainType
from model.Unit import Unit
from model.Vehicle import Vehicle
from model.VehicleType import VehicleType
from model.VehicleUpdate import VehicleUpdate
from model.WeatherType import WeatherType
from model.World import World


DEBUG = True

""" Tuning params """
NUCLEAR_DISTANCE = [100, 300]


class TShirtBot:
    """
        States:
            - init_regroup state (whirlwind)
                .set group for all unites
                .set group for whirlwind and 2 groups for 2 stealth
                .make a whirlwind
            - moving to enemy + whirlwind
            - atomic bomb available
            - atomic bomb against me
            - keep calm and out-scale
                .if less than 10 enemy units in different map places

        enemy_memory:
            - atomic bomb cooldown
            - if atomic bomb enable
            - stealth detector
    """

    def __init__(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self.state = ''

        self.terrain = None
        self.weather = None
        self.orders = deque(maxlen=5000)
        self.current_order_wait = 0
        self.my_center = []
        self.enemy_center = []
        self.my_vehicles = {}
        self.enemy_vehicles = {}

        self._init_variables()

        self.whirlwind_packed = False

    def init_tick(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self._update_vehicles()

        if not self.whirlwind_packed:
            self.state = 'init_regroup'
        if self.whirlwind_packed:
            self.state = 'whirlwind'

    def make_decision(self):
        if self.state == 'init_regroup':
            self.state_regroup()
        if self.state == 'whirlwind':
            self.state_whirlwind()
        if self.state == 'AB':
            pass
        if self.state == 'ENEMY_AB':
            pass
        if self.state is None or self.state == '':
            pass
        return self._execute_command_in_order()

    def state_regroup(self):
        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height)
        self._add_command_to_orders(action=ActionType.SCALE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    factor=0.9, next_delay=80)
        self._add_command_to_orders(action=ActionType.ROTATE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    angle=1.5, next_delay=120)
        self._add_command_to_orders(action=ActionType.ROTATE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    angle=1, next_delay=100)
        self._add_command_to_orders(action=ActionType.SCALE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    factor=0.3, next_delay=20)
        self.whirlwind_packed = True

    def state_whirlwind(self):
        if len(self.orders) == 0:
            self._add_command_to_orders(action=ActionType.ROTATE, angle=1, next_delay=60)
            self._add_command_to_orders(action=ActionType.SCALE, factor=0.1, next_delay=60)
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height)
            self._add_command_to_orders(action=ActionType.MOVE, max_speed=0.3, next_delay=25)

    def _init_variables(self):
        self.terrain = self.world.terrain_by_cell_x_y
        self.weather = self.world.weather_by_cell_x_y

        for vehicle in self.world.new_vehicles:
            if vehicle.player_id == self.me.id:
                self.my_vehicles[vehicle.id] = vehicle
            else:
                self.enemy_vehicles[vehicle.id] = vehicle

    def _update_vehicles(self):
        for vehicle in self.world.vehicle_updates:
            if vehicle.durability == 0:
                if vehicle.id in self.my_vehicles.keys():
                    del self.my_vehicles[vehicle.id]
                else:
                    del self.enemy_vehicles[vehicle.id]
            else:
                if vehicle.id in self.my_vehicles.keys():
                    self.my_vehicles[vehicle.id] = vehicle
                else:
                    self.enemy_vehicles[vehicle.id] = vehicle

    def _add_command_to_orders(self, action, right=0., bottom=0., x=.0, y=.0,
                               factor=1., angle=0., max_speed=1.,
                               next_delay=0):
        temp_command = copy.deepcopy(self.move)
        temp_command.action = action
        temp_command.right = right
        temp_command.bottom = bottom
        temp_command.x = x
        temp_command.y = y
        temp_command.factor = factor
        temp_command.angle = angle
        temp_command.max_speed = max_speed

        self.orders.append(temp_command)
        if DEBUG:
            print('ORDER APPEND: ', action, 'order length: ', len(self.orders))
        if next_delay > 0:
            self.orders.append('wait %s' % next_delay)

    def _execute_command_in_order(self):
        if self.current_order_wait > 0:
            self.current_order_wait -= 1
            return None
        else:
            if len(self.orders) > 0:
                command = self.orders.popleft()
                if type(command) is str:
                    self.current_order_wait += int(command.split(' ')[1])
                    return None
                else:
                    if (command.action == ActionType.MOVE) and (command.x == 0.0) and (command.y == 0.0):
                        self.enemy_center = [np.mean([vehicle.x for vehicle in self.enemy_vehicles.values()]),
                                             np.mean([vehicle.y for vehicle in self.enemy_vehicles.values()])]
                        command.x, command.y = self.enemy_center[0], self.enemy_center[1]
                    if command.action in [ActionType.SCALE, ActionType.ROTATE] and (command.x < 1):
                        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
                        command.x, command.y = self.my_center[0], self.my_center[1]
                    return command
        return None


class MyStrategy:
    my_bot = None

    def game_init(self, world, game, move, me):
        self.my_bot = TShirtBot(world, game, move, me)

    def move(self, me: Player, world: World, game: Game, move: Move):
        if world.tick_index == 0:
            self.game_init(world=world, game=game, move=move, me=me)

        self.my_bot.init_tick(world, game, move, me)
        bot_answer = self.my_bot.make_decision()

        if DEBUG:
            if bot_answer:
                print('ACTION', bot_answer.action, bot_answer.x, bot_answer.y, bot_answer.right, bot_answer.bottom)

        if bot_answer:
            move.action = bot_answer.action
            move.right = bot_answer.right
            move.bottom = bot_answer.bottom
            move.x = bot_answer.x
            move.y = bot_answer.y
            move.factor = bot_answer.factor
            move.max_speed = bot_answer.max_speed
            move.angle = bot_answer.angle
        else:
            move.action = None















