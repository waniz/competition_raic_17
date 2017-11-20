import copy
import numpy as np
import math
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

BOMBER_GROUP = 9
WHIRLWIND_GROUP = 1

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


class NuclearFighter:
    """
        Potential field nuclear bomber
    """

    def __init__(self, group_id, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me
        self.group_id = group_id

        self.state = ''


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
        self.bomberman = None
        self.fighters_exist = True
        self.bomberman_alive = False

        self.terrain = None
        self.weather = None
        self.orders = deque(maxlen=5000)
        self.current_order_wait = 0
        self.my_center = []
        self.enemy_center = []
        self.my_vehicles = {}
        self.my_initial_vehicles = {}
        self.enemy_initial_vehicles = {}
        self.enemy_vehicles = {}

        self._init_variables()

        self.whirlwind_packed = False

    def init_tick(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self._update_vehicles()
        self.my_vehicles = copy.deepcopy(self.my_initial_vehicles)

        if self.me.remaining_action_cooldown_ticks > 0:
            self.state = 'no_action_points'
        elif not self.bomberman_alive and self.fighters_exist:
            self.state = 'init_bomberman'
        elif not self.whirlwind_packed:
            self.state = 'init_regroup'
        # elif self._nuclear_check():
        #     self.state = 'AB'
        elif self.whirlwind_packed:
            self.state = 'whirlwind'

    def make_decision(self):
        if self.state == 'no_action_points':
            self.no_action()
        if self.state == 'init_bomberman':
            self.init_bomberman()
        if self.state == 'init_regroup':
            self.state_regroup()
        if self.state == 'whirlwind':
            self.state_whirlwind()
        if self.state == 'AB':
            self.big_boom()
        if self.state == 'ENEMY_AB':
            pass
        if self.state is None or self.state == '':
            pass
        return self._execute_command_in_order()

    def init_bomberman(self):
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.FIGHTER)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=BOMBER_GROUP)

        fluges = {}
        for vehicle in self.my_initial_vehicles.values():
            if vehicle.type == VehicleType.FIGHTER:
                fluges[vehicle.id] = vehicle
        my_center_fluges = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                            np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
        self._add_command_to_orders(action=ActionType.MOVE, x=(self.world.width / 4) - float(my_center_fluges[0]),
                                    y=self.world.height / 4 - float(my_center_fluges[1]), next_delay=100)
        self._add_command_to_orders(action=ActionType.SCALE, factor=2, next_delay=20,
                                    x=float(my_center_fluges[0]), y=float(my_center_fluges[1]))

        self.bomberman_alive = True

    def state_regroup(self):
        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height)
        self._add_command_to_orders(action=ActionType.DESELECT, group=BOMBER_GROUP)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=WHIRLWIND_GROUP)
        self._add_command_to_orders(action=ActionType.SCALE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    factor=0.1, next_delay=120)
        self._add_command_to_orders(action=ActionType.ROTATE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    angle=1.5, next_delay=120)
        self._add_command_to_orders(action=ActionType.ROTATE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    angle=1, next_delay=100)
        self._add_command_to_orders(action=ActionType.SCALE, x=float(self.my_center[0]), y=float(self.my_center[1]),
                                    factor=0.1, next_delay=40)
        self.whirlwind_packed = True

    def state_whirlwind(self):
        if len(self.orders) == 0:
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=WHIRLWIND_GROUP)
            self._add_command_to_orders(action=ActionType.ROTATE, angle=1, next_delay=60)
            self._add_command_to_orders(action=ActionType.SCALE, factor=0.1, next_delay=60)
            self._add_command_to_orders(action=ActionType.MOVE, max_speed=0.3, next_delay=40)

    def big_boom(self):
        self.current_order_wait = 0
        # self._add_command_to_orders(action=ActionType.TACTICAL_NUCLEAR_STRIKE, x=self.nuclear_x, y=self.nuclear_y,
        #                             vehicle_id=self.vehicle_id_nuclear, priority=True)
        self._add_command_to_orders(action=ActionType.TACTICAL_NUCLEAR_STRIKE,
                                    x=self.nuclear_x,
                                    y=self.nuclear_y,
                                    vehicle_id=self.vehicle_id_nuclear, priority=True)
        # print(list(self.my_vehicles.keys())[0])
        # self._add_command_to_orders(action=ActionType.TACTICAL_NUCLEAR_STRIKE,
        #                             x=self.my_vehicles[list(self.my_vehicles.keys())[0]].x + 20,
        #                             y=self.my_vehicles[list(self.my_vehicles.keys())[0]].y + 20,
        #                             vehicle_id=list(self.my_vehicles.keys())[0], priority=True)

    def no_action(self):
        self.move.action = None

    def _init_variables(self):
        self.terrain = self.world.terrain_by_cell_x_y
        self.weather = self.world.weather_by_cell_x_y

        for vehicle in self.world.new_vehicles:
            if vehicle.player_id == self.me.id:
                self.my_vehicles[vehicle.id] = vehicle
            else:
                self.enemy_vehicles[vehicle.id] = vehicle
        self.my_initial_vehicles = copy.deepcopy(self.my_vehicles)
        self.enemy_initial_vehicles = copy.deepcopy(self.enemy_vehicles)

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

    def _add_command_to_orders(self, action, right=.0, bottom=.0, left=.0, top=.0, x=.0, y=.0,
                               factor=.0, angle=.0, max_speed=.0, vehicle_id=-1, group=0, vehicle_type=None,
                               next_delay=0, priority=False):
        temp_command = copy.deepcopy(self.move)
        temp_command.action = action
        temp_command.right = right
        temp_command.left = left
        temp_command.bottom = bottom
        temp_command.top = top
        temp_command.x = x
        temp_command.y = y
        temp_command.factor = factor
        temp_command.angle = angle
        temp_command.max_speed = max_speed
        temp_command.vehicle_id = vehicle_id
        temp_command.group = group
        if vehicle_type:
            temp_command.vehicle_type = vehicle_type

        if not priority:
            self.orders.append(temp_command)
        else:
            self.orders.appendleft(temp_command)

        if next_delay > 0:
            self.orders.append('wait %s' % next_delay)

    def _execute_command_in_order(self):
        if self.me.remaining_action_cooldown_ticks > 0:
            self.move.action = None
            return self.move.action
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
                        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
                        command.x = self.enemy_center[0] - self.my_center[0]
                        command.y = self.enemy_center[1] - self.my_center[1]
                    if command.action in [ActionType.SCALE, ActionType.ROTATE] and (command.x < 1):
                        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
                        command.x, command.y = self.my_center[0], self.my_center[1]
                    return command
        return None

    def _nuclear_check(self):
        if self.me.remaining_nuclear_strike_cooldown_ticks == 0:
            self.enemy_center = [np.mean([vehicle.x for vehicle in self.enemy_vehicles.values()]),
                                 np.mean([vehicle.y for vehicle in self.enemy_vehicles.values()])]
            self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                              np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
            # distance = math.sqrt((self.my_center[0] - self.enemy_center[0]) ** 2 + (
            #     self.my_center[1] - self.enemy_center[1]) ** 2)
            vehicle_id, vision, min_distance, min_enemy_dist, min_enemy_id = self._get_closest_to_enemy_vehicle()
            if min_enemy_dist <= 100:
                self.nuclear_x = self.enemy_vehicles[min_enemy_id].x
                self.nuclear_y = self.enemy_vehicles[min_enemy_id].y

                self.vehicle_id_nuclear = vehicle_id
                return True
        return False

    def _get_closest_to_enemy_vehicle(self):
        min_distance, best_id = 100000000, -1
        for vehicle in self.my_vehicles.values():
            distance = (vehicle.x - self.enemy_center[0]) ** 2 + (vehicle.y - self.enemy_center[1]) ** 2
            if distance < min_distance:
                min_distance = distance
                best_id = vehicle.id
        min_enemy_dist, min_enemy_id = 100000000, 1
        for enemy in self.enemy_vehicles.values():
            min_enemy = (enemy.x - self.my_vehicles[best_id].x) ** 2 + (enemy.y - self.my_vehicles[best_id].y) ** 2
            if min_enemy < min_enemy_dist:
                min_enemy_dist = min_enemy
                min_enemy_id = enemy.id
        return best_id, self.my_initial_vehicles[best_id].vision_range, math.sqrt(min_distance), \
               math.sqrt(min_enemy_dist), min_enemy_id


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
                print('[EXECUTE: T%s: EXE:%s STATE:%s] %s' % (world.tick_index, self.commands_executed,
                                                              self.my_bot.state, ACTIONS[bot_answer.action]))
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















