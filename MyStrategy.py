import numpy as np
import math
import copy

from collections import deque

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.TerrainType import TerrainType
from model.VehicleType import VehicleType
from model.WeatherType import WeatherType
from model.World import World


""" PARAMS and CONST """
DEBUG = True

DEFAULT_COMMAND = 42

SANDWICH_GROUP = 1
HARASS_GROUP = 2

FIGHTER_GROUP = 3
ARRV_GROUP = 4
HELICOPTER_GROUP = 5
IFV_GROUP = 6
TANK_GROUP = 7

ANTI_NUCLEAR_GROUP = 10

F1_GROUP = 11
F2_GROUP = 12
F3_GROUP = 13
F4_GROUP = 14
F5_GROUP = 15
F6_GROUP = 16
F7_GROUP = 17
F8_GROUP = 18
F9_GROUP = 19
F10_GROUP = 20
F11_GROUP = 21
F12_GROUP = 22
F13_GROUP = 23
F14_GROUP = 24
F15_GROUP = 25
F16_GROUP = 26

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

GROUPS_DEBUG = {
    0: 'NONE_GROUP',
    1: 'SANDWICH_GROUP',
    2: 'HARASS_GROUP',
    3: 'FIGHTER_GROUP',
    4: 'ARRV_GROUP',
    5: 'HELICOPTER_GROUP',
    6: 'IFV_GROUP',
    7: 'TANK_GROUP',
    10: 'ANTI_NUCLEAR_GROUP',
    11: 'F1_GROUP',
    12: 'F2_GROUP',
    13: 'F3_GROUP',
    14: 'F4_GROUP',
    15: 'F5_GROUP',
    16: 'F6_GROUP',
    17: 'F7_GROUP',
    18: 'F8_GROUP',
    19: 'F9_GROUP',
    20: 'F10_GROUP',
    21: 'F11_GROUP',
    22: 'F12_GROUP',
    23: 'F13_GROUP',
    24: 'F14_GROUP',
    25: 'F15_GROUP',
    26: 'F16_GROUP',
}


class Clusters:

    def __init__(self):
        pass


class FighterHarass:

    def __init(self):
        pass


class OrderManager:
    orders = {}
    priorities = {}
    delays = {}
    group_lst = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 42]
    blocker_commands = deque()
    move = None

    def __init__(self):
        for i in range(4):
            self.priorities[i] = deque()

        for i in self.group_lst:
            self.delays[i] = 0

        self.orders[DEFAULT_COMMAND] = deque()

        self.orders[SANDWICH_GROUP] = deque()
        self.orders[HARASS_GROUP] = deque()
        self.orders[FIGHTER_GROUP] = deque()
        self.orders[ARRV_GROUP] = deque()
        self.orders[HELICOPTER_GROUP] = deque()
        self.orders[IFV_GROUP] = deque()
        self.orders[TANK_GROUP] = deque()

        self.orders[ANTI_NUCLEAR_GROUP] = deque()

        self.orders[F1_GROUP] = deque()
        self.orders[F2_GROUP] = deque()
        self.orders[F3_GROUP] = deque()
        self.orders[F4_GROUP] = deque()
        self.orders[F5_GROUP] = deque()
        self.orders[F6_GROUP] = deque()
        self.orders[F7_GROUP] = deque()
        self.orders[F8_GROUP] = deque()
        self.orders[F9_GROUP] = deque()
        self.orders[F10_GROUP] = deque()
        self.orders[F11_GROUP] = deque()
        self.orders[F12_GROUP] = deque()
        self.orders[F13_GROUP] = deque()
        self.orders[F14_GROUP] = deque()
        self.orders[F15_GROUP] = deque()
        self.orders[F16_GROUP] = deque()

    def get_this_tick_command(self):
        for key in self.delays.keys():
            if self.delays[key] > 0:
                self.delays[key] -= 1

        if DEBUG:
            print(self.priorities[2])
            print(self.orders[HELICOPTER_GROUP])
            print(self.orders[FIGHTER_GROUP])

        return self.balancer()

    def set_move(self, move):
        self.move = move

    def balancer(self):
        command = None

        if len(self.priorities[0]) > 0:
            bot_gr = self.priorities[0][0]
            if self.delays[bot_gr] == 0:
                bot_gr = self.priorities[0].popleft()
                command = self.orders[bot_gr].popleft()
                if len(self.orders[bot_gr]) > 0:
                    if type(self.orders[bot_gr][0]) is str:
                        delay_com = self.orders[bot_gr].popleft()
                        self.delays[bot_gr] += int(delay_com.split(' ')[1])
            else:
                if len(self.priorities[0]) > 1:
                    for bgr_pos in range(1, len(self.priorities[0])):
                        if self.delays[self.priorities[0][bgr_pos]] == 0:
                            bot_gr = self.priorities[0][bgr_pos]
                            self.priorities[0].remove(bot_gr)
                            command = self.orders[bot_gr].popleft()
                            if len(self.orders[bot_gr]) > 0:
                                if type(self.orders[bot_gr][0]) is str:
                                    delay_com = self.orders[bot_gr].popleft()
                                    self.delays[bot_gr] += int(delay_com.split(' ')[1])
                            break
            if command:
                return command

        if len(self.priorities[1]) > 0:
            bot_gr = self.priorities[1][0]
            if self.delays[bot_gr] == 0:
                bot_gr = self.priorities[1].popleft()
                command = self.orders[bot_gr].popleft()
                if len(self.orders[bot_gr]) > 0:
                    if type(self.orders[bot_gr][0]) is str:
                        delay_com = self.orders[bot_gr].popleft()
                        self.delays[bot_gr] += int(delay_com.split(' ')[1])
            else:
                if len(self.priorities[1]) > 1:
                    for bgr_pos in range(1, len(self.priorities[1])):
                        if self.delays[self.priorities[1][bgr_pos]] == 0:
                            bot_gr = self.priorities[1][bgr_pos]
                            self.priorities[1].remove(bot_gr)
                            command = self.orders[bot_gr].popleft()
                            if len(self.orders[bot_gr]) > 0:
                                if type(self.orders[bot_gr][0]) is str:
                                    delay_com = self.orders[bot_gr].popleft()
                                    self.delays[bot_gr] += int(delay_com.split(' ')[1])
                            break
            if command:
                return command

        if len(self.priorities[2]) > 0:
            bot_gr = self.priorities[2][0]
            if self.delays[bot_gr] == 0:
                bot_gr = self.priorities[2].popleft()
                command = self.orders[bot_gr].popleft()
                if len(self.orders[bot_gr]) > 0:
                    if type(self.orders[bot_gr][0]) is str:
                        delay_com = self.orders[bot_gr].popleft()
                        self.delays[bot_gr] += int(delay_com.split(' ')[1])
            else:
                if len(self.priorities[2]) > 1:
                    for bgr_pos in range(1, len(self.priorities[2])):
                        if self.delays[self.priorities[2][bgr_pos]] == 0:
                            bot_gr = self.priorities[2][bgr_pos]
                            self.priorities[2].remove(bot_gr)
                            command = self.orders[bot_gr].popleft()
                            if len(self.orders[bot_gr]) > 0:
                                if type(self.orders[bot_gr][0]) is str:
                                    delay_com = self.orders[bot_gr].popleft()
                                    self.delays[bot_gr] += int(delay_com.split(' ')[1])
                            break
            if command:
                return command

        if len(self.priorities[3]) > 0:
            bot_gr = self.priorities[3][0]
            if self.delays[bot_gr] == 0:
                bot_gr = self.priorities[3].popleft()
                command = self.orders[bot_gr].popleft()
                if len(self.orders[bot_gr]) > 0:
                    if type(self.orders[bot_gr][0]) is str:
                        delay_com = self.orders[bot_gr].popleft()
                        self.delays[bot_gr] += int(delay_com.split(' ')[1])
            else:
                if len(self.priorities[3]) > 1:
                    for bgr_pos in range(1, len(self.priorities[3])):
                        if self.delays[self.priorities[3][bgr_pos]] == 0:
                            bot_gr = self.priorities[3][bgr_pos]
                            self.priorities[3].remove(bot_gr)
                            command = self.orders[bot_gr].popleft()
                            if len(self.orders[bot_gr]) > 0:
                                if type(self.orders[bot_gr][0]) is str:
                                    delay_com = self.orders[bot_gr].popleft()
                                    self.delays[bot_gr] += int(delay_com.split(' ')[1])
                            break
            if command:
                return command

        return None

    def add_command(self, group_bot, action, right=.0, bottom=.0, left=.0, top=.0, x=.0, y=.0,
                    factor=.0, angle=.0, max_speed=.0, vehicle_id=-1, group=0, vehicle_type=None, priority=False,
                    delay=0, priority_bot=3):

        self.priorities[priority_bot].append(group_bot)

        temp_command = copy.copy(self.move)
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
        if vehicle_type is not None:
            temp_command.vehicle_type = vehicle_type

        if not priority:
            self.orders[group_bot].append(temp_command)
        else:
            self.orders[group_bot].appendleft(temp_command)

        if delay > 0:
            self.orders[group_bot].append('wait %s' % delay)


class MainBot:
    def __init__(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self.order_manager = OrderManager()
        self.cluster = Clusters()
        self.harass = FighterHarass()

        self.state = ''

        self.terrain = world.terrain_by_cell_x_y
        self.weather = world.weather_by_cell_x_y
        self.my_vehicles = {}
        self.my_initial_vehicles = {}
        self.enemy_initial_vehicles = {}
        self.enemy_vehicles = {}
        self.fighters, self.arrv, self.helicopters, self.ifv, self.tank = {}, {}, {}, {}, {}
        self.factories = {}

        self.orders = deque(maxlen=5000)
        self.my_center = []
        self.enemy_center = []
        self.current_order_wait = 0
        self.nuclear_defence_active = 0

        self.sandwich_packed = False
        if len(self.world.facilities) > 0:
            if DEBUG:
                print('[DEBUG] FACILITY ACTIVE')
            self.factory_active = True
        else:
            if DEBUG:
                print('[DEBUG] FACILITY NOT ACTIVE')
            self.factory_active = False

        self._init_variables()

    def init_tick(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self.order_manager.set_move(self.move)

        self._update_vehicles()
        if world.tick_index == 0:
            self.my_vehicles = self.my_initial_vehicles.copy()

        self.state = ''

        if self.factory_active:
            if self.me.remaining_action_cooldown_ticks != 0:
                self.state = 'R2:no_action_points'
            elif not self.sandwich_packed:
                self.state = 'R2:init_regroup'

        if not self.factory_active:
            if DEBUG:
                print(self.me.remaining_action_cooldown_ticks)
            if self.me.remaining_action_cooldown_ticks != 0:
                self.state = 'R1:no_action_points'
            elif not self.sandwich_packed:
                self.state = 'R1:init_regroup'
            # elif self._nuclear_defence():
            #     self.state = 'R1:nuclear_defence'
            elif self._nuclear_check():
                self.state = 'R1:nuclear_attack'
            elif self.sandwich_packed:
                self.state = 'R1:sandwich'

    def make_decision(self):
        if self.state == 'R2:no_action_points':
            self.state_no_action()

        if self.state == 'R2:init_regroup':
            self.r2_state_regroup()
            return self.order_manager.get_this_tick_command()

        if self.state == 'R1:no_action_points':
            self.state_no_action()
        if self.state == 'R1:init_regroup':
            self.r1_state_regroup()
            return self.order_manager.get_this_tick_command()
        if self.state == 'R1:sandwich':
            self.r1_state_sandwich()
            return self.order_manager.get_this_tick_command()
        if self.state == 'R1:nuclear_attack':
            self.r1_state_nuclear_attack()
            return self.order_manager.get_this_tick_command()
        # if self.state == 'R1:nuclear_defence':
        #     self.state_defence()

        if self.state == '':
            pass

    def state_no_action(self):
        self.move.action = None

    """ R2 section """
    def r2_state_regroup(self):
        self.sandwich_packed = True

        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.FIGHTER, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=FIGHTER_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.ARRV, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=ARRV_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.HELICOPTER, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=HELICOPTER_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.IFV, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=IFV_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.TANK, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=TANK_GROUP, priority_bot=1)
        #
        # self.order_manager.add_command(group_bot=FIGHTER_GROUP, action=ActionType.CLEAR_AND_SELECT,
        #                                right=self.world.width, bottom=self.world.height, group=FIGHTER_GROUP,
        #                                priority_bot=3)
        # self.order_manager.add_command(group_bot=FIGHTER_GROUP, action=ActionType.MOVE, x=300, y=300, priority_bot=2)

        """ get centers """
        for vehicle in self.my_vehicles.values():
            if vehicle.type == VehicleType.FIGHTER:
                self.fighters[vehicle.id] = vehicle
            if vehicle.type == VehicleType.TANK:
                self.tank[vehicle.id] = vehicle
            if vehicle.type == VehicleType.IFV:
                self.ifv[vehicle.id] = vehicle
            if vehicle.type == VehicleType.HELICOPTER:
                self.helicopters[vehicle.id] = vehicle
            if vehicle.type == VehicleType.ARRV:
                self.arrv[vehicle.id] = vehicle
        fighter_center = [np.mean([vehicle.x for vehicle in self.fighters.values()]),
                          np.mean([vehicle.y for vehicle in self.fighters.values()])]
        tank_center = [np.mean([vehicle.x for vehicle in self.tank.values()]),
                       np.mean([vehicle.y for vehicle in self.tank.values()])]
        ifv_center = [np.mean([vehicle.x for vehicle in self.ifv.values()]),
                      np.mean([vehicle.y for vehicle in self.ifv.values()])]
        helicopters_center = [np.mean([vehicle.x for vehicle in self.helicopters.values()]),
                              np.mean([vehicle.y for vehicle in self.helicopters.values()])]
        arrv_center = [np.mean([vehicle.x for vehicle in self.arrv.values()]),
                       np.mean([vehicle.y for vehicle in self.arrv.values()])]

        """ calculate position """
        pos_unit, pos_units_fly, pos_units_ground = {}, {}, {}
        pos = 0
        for xy in [[45.0, 45.0], [119.0, 45.0], [193.0, 45.0],
                   [45.0, 119.0], [119.0, 119.0], [193.0, 119.0],
                   [45.0, 193.0], [119.0, 193.0], [193.0, 193.0]]:
            pos += 1
            if fighter_center[0] == xy[0] and fighter_center[1] == xy[1]:
                pos_unit['fighter'] = pos
                pos_units_fly['fighter'] = pos
            if tank_center[0] == xy[0] and tank_center[1] == xy[1]:
                pos_unit['tank'] = pos
                pos_units_ground['tank'] = pos
            if ifv_center[0] == xy[0] and ifv_center[1] == xy[1]:
                pos_unit['ifv'] = pos
                pos_units_ground['ifv'] = pos
            if helicopters_center[0] == xy[0] and helicopters_center[1] == xy[1]:
                pos_unit['helicopters'] = pos
                pos_units_fly['helicopters'] = pos
            if arrv_center[0] == xy[0] and arrv_center[1] == xy[1]:
                pos_unit['arrv'] = pos
                pos_units_ground['arrv'] = pos
        if DEBUG:
            print(pos_unit)
    """ /R2 section """

    """ R1 section """
    def r1_state_regroup(self):
        self.sandwich_packed = True

        self._initial_group_sandwich()

        pos_unit, pos_units_fly, pos_units_ground = self._init_centers_and_pos()

        """ fly units regroup """
        self._fly_phalanx(pos_unit, pos_units_fly, pos_units_ground)

        """ calculate ground movements """
        if (pos_unit['tank'] in [4, 5, 6]) and (pos_unit['ifv'] in [4, 5, 6]) and (pos_unit['arrv'] in [4, 5, 6]):
            if DEBUG:
                print('3 in middle')
            pass

        # ifv location (if 2 in middle)
        if (pos_unit['ifv'] not in [4, 5, 6]) and (pos_unit['arrv'] in [4, 5, 6]) and (pos_unit['tank'] in [4, 5, 6]):
            ifv_pos = [4, 5, 6]
            ifv_pos.remove(pos_unit['arrv'])
            ifv_pos.remove(pos_unit['tank'])
            if DEBUG:
                print('2 in of middle / IFV', ifv_pos)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 1:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 7:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 2:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 8:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 3:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-148, y=0, delay=460)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 9:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-148, y=0, delay=460)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 1:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 7:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 2:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 8:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 3:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 9:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 1:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=148, y=0, delay=460)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 7:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=148, y=0, delay=460)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 2:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 8:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 3:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 9:
                self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)

        # arrv location (if 2 in middle)
        if (pos_unit['arrv'] not in [4, 5, 6]) and (pos_unit['ifv'] in [4, 5, 6]) and (pos_unit['tank'] in [4, 5, 6]):
            arrv_pos = [4, 5, 6]
            arrv_pos.remove(pos_unit['ifv'])
            arrv_pos.remove(pos_unit['tank'])
            if DEBUG:
                print('2 in of middle / ARRV', arrv_pos)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 1:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 7:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 2:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 8:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 3:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-148, y=0, delay=460)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 9:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-148, y=0, delay=460)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 1:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 7:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 2:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 8:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 3:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 9:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 1:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=148, y=0, delay=460)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 7:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=148, y=0, delay=460)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 2:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 8:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 3:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 9:
                self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)

        # tank location (if 2 in middle)
        if (pos_unit['tank'] not in [4, 5, 6]) and (pos_unit['ifv'] in [4, 5, 6]) and (pos_unit['arrv'] in [4, 5, 6]):
            tank_pos = [4, 5, 6]
            tank_pos.remove(pos_unit['ifv'])
            tank_pos.remove(pos_unit['arrv'])
            if DEBUG:
                print('2 in of middle / TANK', tank_pos)
            if tank_pos[0] == 4 and pos_unit['tank'] == 1:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 7:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 2:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 8:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 3:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-148, y=0, delay=600)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 9:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-148, y=0, delay=600)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 1:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 7:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 2:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 8:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 3:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 9:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 1:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=148, y=0, delay=600)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 7:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=148, y=0, delay=600)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 2:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 8:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 3:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 9:
                self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)

        # all 3 not in middle
        if (pos_unit['tank'] in [1, 2, 3]) and (pos_unit['ifv'] in [1, 2, 3]) and (pos_unit['arrv'] in [1, 2, 3]):
            if DEBUG:
                print('3 not in middle 123')
            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
        elif (pos_unit['tank'] in [7, 8, 9]) and (pos_unit['ifv'] in [7, 8, 9]) and (pos_unit['arrv'] in [7, 8, 9]):
            if DEBUG:
                print('3 not in middle 789')
            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
        elif (pos_unit['tank'] in [1, 2, 3, 7, 8, 9]) and (pos_unit['ifv'] in [1, 2, 3, 7, 8, 9]) \
                and (pos_unit['arrv'] in [1, 2, 3, 7, 8, 9]):
            vehicle_places = []
            vehicle_places.append(pos_unit['tank'])
            vehicle_places.append(pos_unit['arrv'])
            vehicle_places.append(pos_unit['ifv'])
            occupyed_places = []
            if DEBUG:
                print('3 not in middle diff', vehicle_places)
            if 1 in vehicle_places:
                if DEBUG:
                    print('1')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 1:
                        group_inside = key
                if group_inside == 'tank':
                    self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
                if group_inside == 'arrv':
                    self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
                if group_inside == 'ifv':
                    self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
                occupyed_places.append(4)
            if 2 in vehicle_places:
                if DEBUG:
                    print('2')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 2:
                        group_inside = key
                if group_inside == 'tank':
                    self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
                if group_inside == 'arrv':
                    self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
                if group_inside == 'ifv':
                    self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
                occupyed_places.append(5)
            if 3 in vehicle_places:
                if DEBUG:
                    print('3')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 3:
                        group_inside = key
                if group_inside == 'tank':
                    self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=74, delay=300)
                if group_inside == 'arrv':
                    self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=74, delay=230)
                if group_inside == 'ifv':
                    self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=74, delay=230)
                occupyed_places.append(6)
            if 8 in vehicle_places:
                if DEBUG:
                    print('8')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 8:
                        group_inside = key
                if 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(5)
                else:
                    if 4 not in occupyed_places and 7 not in vehicle_places:
                        if group_inside == 'tank':
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                        if group_inside == 'arrv':
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                        if group_inside == 'ifv':
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                        occupyed_places.append(5)
                    elif 4 not in occupyed_places and 9 not in vehicle_places:
                        if group_inside == 'tank':
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                        if group_inside == 'arrv':
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                        if group_inside == 'ifv':
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                        occupyed_places.append(5)
                    elif 6 not in occupyed_places:
                        if group_inside == 'tank':
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                            self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                        if group_inside == 'arrv':
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                            self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                        if group_inside == 'ifv':
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                            self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                        occupyed_places.append(5)
            if 7 in vehicle_places:
                if DEBUG:
                    print('7')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 7:
                        group_inside = key
                if 4 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=74, y=0, delay=300)
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=74, y=0, delay=230)
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=74, y=0, delay=230)
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(5)
                elif 6 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=148, y=0, delay=600)
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=148, y=0, delay=460)
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=148, y=0, delay=460)
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(6)
            if 9 in vehicle_places:
                if DEBUG:
                    print('9')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 9:
                        group_inside = key
                if 6 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-74, y=0, delay=300)
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-74, y=0, delay=230)
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-74, y=0, delay=230)
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(5)
                elif 4 not in occupyed_places:
                    if group_inside == 'tank':
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=-148, y=0, delay=600)
                        self._unit_move(group_bot=TANK_GROUP, group=TANK_GROUP, x=0, y=-74, delay=300)
                    if group_inside == 'arrv':
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=-148, y=0, delay=460)
                        self._unit_move(group_bot=ARRV_GROUP, group=ARRV_GROUP, x=0, y=-74, delay=230)
                    if group_inside == 'ifv':
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=-148, y=0, delay=460)
                        self._unit_move(group_bot=IFV_GROUP, group=IFV_GROUP, x=0, y=-74, delay=230)
                    occupyed_places.append(6)

        # all 3 not in middle
        if (pos_unit['tank'] in [1, 2, 3]) and (pos_unit['ifv'] in [1, 2, 3]) and (pos_unit['arrv'] in [1, 2, 3]):
            if DEBUG:
                print('3 not in middle 123')
            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                           x=0, y=74, priority_bot=2, delay=300)
            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                           x=0, y=74, priority_bot=2)
            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                           x=0, y=74, priority_bot=2)
        elif (pos_unit['tank'] in [7, 8, 9]) and (pos_unit['ifv'] in [7, 8, 9]) and (pos_unit['arrv'] in [7, 8, 9]):
            if DEBUG:
                print('3 not in middle 789')
            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                           x=0, y=-74, priority_bot=2, delay=300)
            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                           x=0, y=-74, priority_bot=2)
            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                           x=0, y=-74, priority_bot=2)
        elif (pos_unit['tank'] in [1, 2, 3, 7, 8, 9]) and (pos_unit['ifv'] in [1, 2, 3, 7, 8, 9]) \
                and (pos_unit['arrv'] in [1, 2, 3, 7, 8, 9]):
            vehicle_places = []
            vehicle_places.append(pos_unit['tank'])
            vehicle_places.append(pos_unit['arrv'])
            vehicle_places.append(pos_unit['ifv'])
            occupyed_places = []
            if DEBUG:
                print('3 not in middle diff', vehicle_places)
            if 1 in vehicle_places:
                if DEBUG:
                    print('1')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 1:
                        group_inside = key
                if group_inside == 'tank':
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=TANK_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=300)
                if group_inside == 'arrv':
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2)
                if group_inside == 'ifv':
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=IFV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=230)
                occupyed_places.append(4)
            if 2 in vehicle_places:
                if DEBUG:
                    print('2')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 2:
                        group_inside = key
                if group_inside == 'tank':
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=TANK_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=300)
                if group_inside == 'arrv':
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=230)
                if group_inside == 'ifv':
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=IFV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=230)
                occupyed_places.append(5)
            if 3 in vehicle_places:
                if DEBUG:
                    print('3')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 3:
                        group_inside = key
                if group_inside == 'tank':
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=TANK_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=300)
                if group_inside == 'arrv':
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=230)
                if group_inside == 'ifv':
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                   right=self.world.width, group=IFV_GROUP, priority_bot=2)
                    self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=230)
                occupyed_places.append(6)
            if 8 in vehicle_places:
                if DEBUG:
                    print('8')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 8:
                        group_inside = key
                if 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(5)
                else:
                    if 4 not in occupyed_places and 7 not in vehicle_places:
                        if group_inside == 'tank':
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=-74, y=0, priority_bot=2, delay=300)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=300)
                        if group_inside == 'arrv':
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=-74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        if group_inside == 'ifv':
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=-74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        occupyed_places.append(5)
                    elif 4 not in occupyed_places and 9 not in vehicle_places:
                        if group_inside == 'tank':
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=300)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=300)
                        if group_inside == 'arrv':
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        if group_inside == 'ifv':
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        occupyed_places.append(5)
                    elif 6 not in occupyed_places:
                        if group_inside == 'tank':
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=300)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=TANK_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=300)
                        if group_inside == 'arrv':
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        if group_inside == 'ifv':
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=74, y=0, priority_bot=2, delay=230)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                           right=self.world.width, group=IFV_GROUP, priority_bot=2)
                            self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                           x=0, y=-74, priority_bot=2, delay=230)
                        occupyed_places.append(5)
            if 7 in vehicle_places:
                if DEBUG:
                    print('7')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 7:
                        group_inside = key
                if 4 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(5)
                elif 6 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=600)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=460)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=480)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(6)
            if 9 in vehicle_places:
                if DEBUG:
                    print('9')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 9:
                        group_inside = key
                if 6 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=-74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=-74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=-74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(5)
                elif 4 not in occupyed_places:
                    if group_inside == 'tank':
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=-148, y=0, priority_bot=2, delay=600)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if group_inside == 'arrv':
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=-148, y=0, priority_bot=2, delay=460)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if group_inside == 'ifv':
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=-148, y=0, priority_bot=2, delay=460)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    occupyed_places.append(6)

        # 2 groups out of middle, 1 in middle
        counter = 0
        if pos_unit['tank'] in [4, 5, 6]:
            counter += 1
        if pos_unit['ifv'] in [4, 5, 6]:
            counter += 1
        if pos_unit['arrv'] in [4, 5, 6]:
            counter += 1
        if counter == 1:
            if DEBUG:
                print('2 out of middle', pos_units_ground)
            if 4 in pos_units_ground.values():
                if DEBUG:
                    print('4 in pos_units_ground:')
                if 1 in pos_units_ground.values() and 2 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 2 in pos_units_ground')
                    if pos_unit['tank'] == 4:
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ADD_TO_SELECTION,
                                                       right=self.world.width,
                                                       bottom=self.world.height, group=ARRV_GROUP)
                    if pos_unit['arrv'] == 4:
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ADD_TO_SELECTION,
                                                       right=self.world.width,
                                                       bottom=self.world.height, group=IFV_GROUP)
                    if pos_unit['ifv'] == 4:
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ADD_TO_SELECTION,
                                                       right=self.world.width,
                                                       bottom=self.world.height, group=ARRV_GROUP)
                    self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.MOVE,
                                                   x=74, y=0, priority_bot=2, delay=300)
                    self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.MOVE,
                                                   x=0, y=74, priority_bot=2, delay=300)

                elif 1 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 1:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 1:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                    if pos_unit['tank'] == 3:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 3:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 3:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)

                elif 1 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 1:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 1:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['tank'] == 7:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=600)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)

                    if pos_unit['arrv'] == 7:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=460)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)

                    if pos_unit['ifv'] == 7:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=148, y=0, priority_bot=2, delay=460)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)

                elif 1 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 1:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 1:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['tank'] == 8:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 8:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 8:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=-74, priority_bot=2, delay=230)

                elif 1 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=300)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=TANK_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=TANK_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=300)
                    if pos_unit['arrv'] == 1:
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=ARRV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=ARRV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['ifv'] == 1:
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=74, y=0, priority_bot=2, delay=230)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.CLEAR_AND_SELECT,
                                                       right=self.world.width, group=IFV_GROUP, priority_bot=2)
                        self.order_manager.add_command(group_bot=IFV_GROUP, action=ActionType.MOVE,
                                                       x=0, y=74, priority_bot=2, delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 2 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 7 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 4:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    if pos_unit['arrv'] == 4:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                    if pos_unit['ifv'] == 4:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                elif 7 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 8 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('8 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            elif 5 in pos_units_ground.values():
                if DEBUG:
                    print('5 in pos_units_ground:')
                if 1 in pos_units_ground.values() and 2 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 2 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 1 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 1 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=550)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 1 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 1 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 2 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=550)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 7 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 7 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 8 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('8 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            elif 6 in pos_units_ground.values():
                if DEBUG:
                    print('6 in pos_units_ground:')
                if 1 in pos_units_ground.values() and 2 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 2 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 1 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                elif 1 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 1 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 1 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    if pos_unit['arrv'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                    if pos_unit['ifv'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                elif 2 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 2 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('2 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 2:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 3 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('3 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=550)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 7 in pos_units_ground.values() and 8 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 8 in pos_units_ground')
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 8:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 7 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('7 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 7:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['tank'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if pos_unit['arrv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if pos_unit['ifv'] == 9:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                elif 8 in pos_units_ground.values() and 9 in pos_units_ground.values():
                    if DEBUG:
                        print('8 in pos_units_ground and 9 in pos_units_ground')
                    if pos_unit['tank'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    if pos_unit['arrv'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                    if pos_unit['ifv'] == 6:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.ADD_TO_SELECTION, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)


    # def r1_state_regroup_old(self):


   #

    pass
    #     """ move all units in geometry """
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=96, next_delay=50)
    #
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=96)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-68, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=98, right=1024, bottom=102)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-54, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=102, right=1024, bottom=106)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-40, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=106, right=1024, bottom=110)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-28, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=110, right=1024, bottom=120)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-14, next_delay=16)
    #
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=144, right=1024, bottom=146)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=54, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=138, right=1024, bottom=143)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=40, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=132, right=1024, bottom=137)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=28, next_delay=16)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=126, right=1024, bottom=131)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=14, next_delay=150)
    #
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=72, bottom=1024)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-5, next_delay=32)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=150, top=0, right=1024, bottom=1024)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=0, y=5, next_delay=32)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=72, bottom=1024)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=10)
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=150, top=0, right=1024, bottom=1024)
    #     self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
    #
    #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=1024)
    #     self._add_command_to_orders(action=ActionType.SCALE, x=119, y=119, factor=0.2, next_delay=120)
    #     self._add_command_to_orders(action=ActionType.ROTATE, x=119, y=119, angle=0.9, next_delay=240)
    pass

    def r1_state_sandwich(self):
        # if len(self.orders) == 0:
        #     self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=1024, bottom=1024)
        #     self._add_command_to_orders(action=ActionType.SCALE, factor=0.2, next_delay=40)
        #     self._add_command_to_orders(action=ActionType.MOVE, max_speed=0.2, next_delay=60)
        pass

    def r1_state_nuclear_attack(self):
        self.current_order_wait = 0
        if DEBUG:
            print('NUCLEAR TEST:')
            print(self.nuclear_x, self.nuclear_y, self.vehicle_id_nuclear)
            print(self.my_vehicles[self.vehicle_id_nuclear].x, self.my_vehicles[self.vehicle_id_nuclear].y)
            print(self.enemy_center)
        self._add_command_to_orders(action=ActionType.TACTICAL_NUCLEAR_STRIKE, x=self.nuclear_x, y=self.nuclear_y,
                                    vehicle_id=self.vehicle_id_nuclear, priority=True)

    def state_defence(self):
        attack_x = self.me.next_nuclear_strike_x
        attack_y = self.me.next_nuclear_strike_y
        ticks_before = self.me.next_nuclear_strike_tick_index

        self.nuclear_defence_active = ticks_before - self.world.tick_index

        if DEBUG:
            print('NUCLEAR DEFENCE', attack_x, attack_y, ticks_before)

        self.current_order_wait = 0
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, priority=True)
        self._add_command_to_orders(action=ActionType.SCALE, x=attack_x, y=attack_y,
                                    factor=3, priority=True, next_delay=ticks_before)
        self._add_command_to_orders(action=ActionType.SCALE, x=attack_x, y=attack_y,
                                    factor=0.2, priority=True, next_delay=ticks_before)
    """ /R1 section """

    """ regroup init & movement section """
    def _initial_group_sandwich(self):
        """ add groups """
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.FIGHTER, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=FIGHTER_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.ARRV, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=ARRV_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.HELICOPTER, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=HELICOPTER_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.IFV, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=IFV_GROUP, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, bottom=self.world.height,
                                       vehicle_type=VehicleType.TANK, priority_bot=1)
        self.order_manager.add_command(group_bot=DEFAULT_COMMAND, action=ActionType.ASSIGN,
                                       group=TANK_GROUP, priority_bot=1)

    def _init_centers_and_pos(self):
        """ get centers """
        for vehicle in self.my_vehicles.values():
            if vehicle.type == VehicleType.FIGHTER:
                self.fighters[vehicle.id] = vehicle
            if vehicle.type == VehicleType.TANK:
                self.tank[vehicle.id] = vehicle
            if vehicle.type == VehicleType.IFV:
                self.ifv[vehicle.id] = vehicle
            if vehicle.type == VehicleType.HELICOPTER:
                self.helicopters[vehicle.id] = vehicle
            if vehicle.type == VehicleType.ARRV:
                self.arrv[vehicle.id] = vehicle
        fighter_center = [np.mean([vehicle.x for vehicle in self.fighters.values()]),
                          np.mean([vehicle.y for vehicle in self.fighters.values()])]
        tank_center = [np.mean([vehicle.x for vehicle in self.tank.values()]),
                       np.mean([vehicle.y for vehicle in self.tank.values()])]
        ifv_center = [np.mean([vehicle.x for vehicle in self.ifv.values()]),
                      np.mean([vehicle.y for vehicle in self.ifv.values()])]
        helicopters_center = [np.mean([vehicle.x for vehicle in self.helicopters.values()]),
                              np.mean([vehicle.y for vehicle in self.helicopters.values()])]
        arrv_center = [np.mean([vehicle.x for vehicle in self.arrv.values()]),
                       np.mean([vehicle.y for vehicle in self.arrv.values()])]

        """ calculate position """
        pos_unit, pos_units_fly, pos_units_ground = {}, {}, {}
        pos = 0
        for xy in [[45.0, 45.0], [119.0, 45.0], [193.0, 45.0],
                   [45.0, 119.0], [119.0, 119.0], [193.0, 119.0],
                   [45.0, 193.0], [119.0, 193.0], [193.0, 193.0]]:
            pos += 1
            if fighter_center[0] == xy[0] and fighter_center[1] == xy[1]:
                pos_unit['fighter'] = pos
                pos_units_fly['fighter'] = pos
            if tank_center[0] == xy[0] and tank_center[1] == xy[1]:
                pos_unit['tank'] = pos
                pos_units_ground['tank'] = pos
            if ifv_center[0] == xy[0] and ifv_center[1] == xy[1]:
                pos_unit['ifv'] = pos
                pos_units_ground['ifv'] = pos
            if helicopters_center[0] == xy[0] and helicopters_center[1] == xy[1]:
                pos_unit['helicopters'] = pos
                pos_units_fly['helicopters'] = pos
            if arrv_center[0] == xy[0] and arrv_center[1] == xy[1]:
                pos_unit['arrv'] = pos
                pos_units_ground['arrv'] = pos
        if DEBUG:
            print(pos_unit)
        return pos_unit, pos_units_fly, pos_units_ground

    def _fly_phalanx(self, pos_unit, pos_units_fly, pos_units_ground):
        if pos_unit['fighter'] in [4, 5, 6] and pos_unit['helicopters'] in [4, 5, 6]:
            pass

        if pos_unit['fighter'] not in [4, 5, 6] and pos_unit['helicopters'] in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] not in [4, 5, 6] and pos_unit[helicopters] in [4, 5, 6]')
            if pos_unit['helicopters'] == 4:
                if DEBUG:
                    print('heli 4')
                if pos_unit['fighter'] in [2, 3]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [8, 9]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
                if pos_unit['fighter'] in [1]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [7]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 5:
                if DEBUG:
                    print('heli 5')
                if pos_unit['fighter'] in [1, 3]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [7, 9]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
                if pos_unit['fighter'] in [2]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0, delay=62)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [8]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0, delay=62)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 6:
                if DEBUG:
                    print('heli 6')
                if pos_unit['fighter'] in [1, 2]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [7, 8]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
                if pos_unit['fighter'] in [3]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=-74, y=0, delay=62)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
                if pos_unit['fighter'] in [9]:
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=-74, y=0, delay=62)
                    self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
        if pos_unit['fighter']in [4, 5, 6] and pos_unit['helicopters'] not in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] in [4, 5, 6] and pos_unit[helicopters] not in [4, 5, 6]')
            if pos_unit['fighter'] == 4:
                if DEBUG:
                    print('fighter 4')
                if pos_unit['helicopters'] in [2, 3]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [8, 9]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                if pos_unit['helicopters'] in [1]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [7]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
            elif pos_unit['fighter'] == 5:
                if DEBUG:
                    print('fighter 5')
                if pos_unit['helicopters'] in [1, 3]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [7, 9]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                if pos_unit['helicopters'] in [2]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [8]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
            elif pos_unit['fighter'] == 6:
                if DEBUG:
                    print('fighter 6')
                if pos_unit['helicopters'] in [1, 2]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [7, 8]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                if pos_unit['helicopters'] in [3]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=-74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                if pos_unit['helicopters'] in [9]:
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=-74, y=0, delay=100)
                    self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)

        if pos_unit['fighter'] not in [4, 5, 6] and pos_unit['helicopters'] not in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] not in [4, 5, 6] and pos_unit[helicopters] not in [4, 5, 6]')
            if pos_unit['fighter'] in [1, 2, 3] and pos_unit['helicopters'] in [1, 2, 3]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)

            elif pos_unit['fighter'] in [7, 8, 9] and pos_unit['helicopters'] in [7, 8, 9]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['fighter'] == 1 and pos_unit['helicopters'] == 7:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['fighter'] == 1 and pos_unit['helicopters'] in [8, 9]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
            elif pos_unit['fighter'] == 2 and pos_unit['helicopters'] in [7, 9]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
            elif pos_unit['fighter'] == 3 and pos_unit['helicopters'] in [7, 8]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
            elif pos_unit['fighter'] == 2 and pos_unit['helicopters'] == 8:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
            elif pos_unit['fighter'] == 3 and pos_unit['helicopters'] == 9:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=-74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=-74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=74)
            elif pos_unit['helicopters'] == 1 and pos_unit['fighter'] == 7:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 1 and pos_unit['fighter'] in [8, 9]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 2 and pos_unit['fighter'] in [7, 9]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 3 and pos_unit['fighter'] in [7, 8]:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 2 and pos_unit['fighter'] == 8:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)
            elif pos_unit['helicopters'] == 3 and pos_unit['fighter'] == 9:
                self._unit_move(group_bot=HELICOPTER_GROUP, group=HELICOPTER_GROUP, x=0, y=74)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=-74, y=0)
                self._unit_move(group_bot=FIGHTER_GROUP, group=FIGHTER_GROUP, x=0, y=-74)

    def _unit_move(self, group_bot, group, x, y, delay=0, priority=2):
        self.order_manager.add_command(group_bot=group_bot, action=ActionType.CLEAR_AND_SELECT,
                                       right=self.world.width, group=group, priority_bot=priority)
        self.order_manager.add_command(group_bot=group_bot, action=ActionType.MOVE,
                                       x=x, y=y, priority_bot=priority, delay=delay)
    """ /regroup init & movement section """

    """ init & update section """
    def _init_variables(self):
        self.terrain = self.world.terrain_by_cell_x_y
        self.weather = self.world.weather_by_cell_x_y

        for vehicle in self.world.new_vehicles:
            if vehicle.player_id == self.me.id:
                self.my_vehicles[vehicle.id] = vehicle
            else:
                self.enemy_vehicles[vehicle.id] = vehicle
        self.my_initial_vehicles = self.my_vehicles.copy()
        self.enemy_initial_vehicles = self.enemy_vehicles.copy()

        if self.factory_active:
            for factory in self.world.facilities:
                self.factories[factory.id] = factory

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
    """ /init & update section """

    """ nuclear section """
    def _nuclear_check(self):
        if self.world.tick_index < 2000:
            return False
        if self.me.remaining_nuclear_strike_cooldown_ticks > 0:
            return False
        self.enemy_center = [np.mean([vehicle.x for vehicle in self.enemy_vehicles.values()]),
                             np.mean([vehicle.y for vehicle in self.enemy_vehicles.values()])]
        self.my_center = [np.mean([vehicle.x for vehicle in self.my_vehicles.values()]),
                          np.mean([vehicle.y for vehicle in self.my_vehicles.values()])]
        enemy_to_center_distance, enemy_id = self._closest_enemy_vehicle()
        if enemy_id == -1:
            return False
        if enemy_to_center_distance > 250:
            return False
        my_unit_to_enemy_distance, unit_id = self._closest_my_vehicle_to_enemy(enemy_id)
        if unit_id == -1:
            return False
        init_vision = self.my_initial_vehicles[unit_id].vision_range
        vision = init_vision
        cell = [math.floor(self.my_vehicles[unit_id].x / 32), math.floor(self.my_vehicles[unit_id].y / 32)]

        if self.my_initial_vehicles[unit_id].aerial:
            weather = self.weather[cell[0]][cell[1]]
            if weather == WeatherType.CLEAR:
                vision = init_vision * 1
            if weather == WeatherType.CLOUD:
                vision = init_vision * 0.8
            if weather == WeatherType.RAIN:
                vision = init_vision * 0.6
        else:
            terrain = self.terrain[cell[0]][cell[1]]
            if terrain == TerrainType.PLAIN:
                vision = init_vision * 1
            if terrain == TerrainType.SWAMP:
                vision = init_vision * 1
            if terrain == TerrainType.FOREST:
                vision = init_vision * 0.8

        if my_unit_to_enemy_distance < vision - 3:
            self.nuclear_x = self.enemy_vehicles[enemy_id].x
            self.nuclear_y = self.enemy_vehicles[enemy_id].y
            self.vehicle_id_nuclear = unit_id
            return True
        return False

    def _closest_my_vehicle_to_enemy_center(self):
        closest_id, closest_dist = -1, 100000000000
        for vehicle in self.my_vehicles.values():
            distance = (vehicle.x - self.enemy_center[0]) ** 2 + (vehicle.y - self.enemy_center[1]) ** 2
            if distance < closest_dist:
                closest_dist = distance
                closest_id = vehicle.id
        return math.sqrt(closest_dist), closest_id

    def _closest_enemy_vehicle(self):
        closest_id, closest_dist = -1, 100000000000
        for vehicle in self.enemy_vehicles.values():
            distance = (vehicle.x - self.my_center[0]) ** 2 + (vehicle.y - self.my_center[1]) ** 2
            if distance < closest_dist:
                closest_dist = distance
                closest_id = vehicle.id
        return math.sqrt(closest_dist), closest_id

    def _closest_my_vehicle_to_enemy(self, enemy_id):
        enemy_center = [self.enemy_vehicles[enemy_id].x, self.enemy_vehicles[enemy_id].y]
        closest_id, closest_dist = -1, 100000000000
        for vehicle in self.my_vehicles.values():
            distance = (vehicle.x - enemy_center[0]) ** 2 + (vehicle.y - enemy_center[1]) ** 2
            if distance < closest_dist:
                closest_dist = distance
                closest_id = vehicle.id
        return math.sqrt(closest_dist), closest_id

    def _nuclear_defence(self):
        if DEBUG:
            if self.nuclear_defence_active > 0:
                print('DEFENCE COOLDOWN %s' % self.nuclear_defence_active)
        if self.me.next_nuclear_strike_tick_index == -1:
            return False
        if self.nuclear_defence_active > 0:
            self.nuclear_defence_active -= 1
            return False
        # if self.me.next_nuclear_strike_vehicle_id in self.my_vehicles.keys():
        #     return False
        return True
    """ /nuclear section """

class MyStrategy:
    my_bot = None
    commands_executed = 0

    def game_init(self, world, game, move, me):
        self.my_bot = MainBot(world, game, move, me)

    def move(self, me: Player, world: World, game: Game, move: Move):
        if world.tick_index == 0:
            self.game_init(world=world, game=game, move=move, me=me)

        self.my_bot.init_tick(world, game, move, me)
        bot_answer = self.my_bot.make_decision()

        if bot_answer:
            self.commands_executed += 1
            if DEBUG:
                print('[EXE: T%s: C#:%s STATE:%s] Action:%s Group:%s, x:%s, y:%s' % (
                    world.tick_index, self.commands_executed, self.my_bot.state, ACTIONS[bot_answer.action],
                    bot_answer.group, bot_answer.x, bot_answer.y))
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
            if DEBUG:
                print('[EXE: T%s: C#:%s STATE:%s] Action:NONE' % (
                    world.tick_index, self.commands_executed, self.my_bot.state))
            move.action = None
