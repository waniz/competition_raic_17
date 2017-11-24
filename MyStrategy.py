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


DEBUG = False

BOMBER_GROUP = 9
WHIRLWIND_GROUP = 1

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
        self.fighters, self.arrv, self.helicopters, self.ifv, self.tank = {}, {}, {}, {}, {}

        self._init_variables()

        self.whirlwind_packed = False

    def init_tick(self, world, game, move, me):
        self.world = world
        self.game = game
        self.move = move
        self.me = me

        self._update_vehicles()
        if world.tick_index == 0:
            self.my_vehicles = self.my_initial_vehicles.copy()

        self.state = ''

        if self.me.remaining_action_cooldown_ticks > 0:
            self.state = 'no_action_points'
        elif not self.whirlwind_packed:
            self.state = 'init_regroup'
        # elif self._nuclear_defence():
        #     self.state = 'nuclear_defence'
        elif self._nuclear_check() and self.world.tick_index > 100:
            self.state = 'nuclear_attack'
        elif self.whirlwind_packed:
            self.state = 'sandwich'

    def make_decision(self):
        if self.state == 'no_action_points':
            self.no_action()
        if self.state == 'init_regroup':
            self.state_regroup()
        if self.state == 'sandwich':
            self.state_whirlwind()
        if self.state == 'nuclear_attack':
            self.big_boom()
        # if self.state == 'nuclear_defence':
        #     self.state_defence()
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

    def state_regroup_old(self):
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

    def state_regroup(self):
        self.whirlwind_packed = True

        """ 10 actions """
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.FIGHTER)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=FIGHTER_GROUP)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.ARRV)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=ARRV_GROUP)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.HELICOPTER)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=HELICOPTER_GROUP)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.IFV)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=IFV_GROUP)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, vehicle_type=VehicleType.TANK)
        self._add_command_to_orders(action=ActionType.ASSIGN, group=TANK_GROUP)

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
        if DEBUG:
            print(fighter_center)
            print(tank_center)
            print(ifv_center)
            print(helicopters_center)
            print(arrv_center)
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

        """ fly units regroup """
        if pos_unit['fighter'] in [4, 5, 6] and pos_unit['helicopters'] in [4, 5, 6]:
            pass

        if pos_unit['fighter'] not in [4, 5, 6] and pos_unit['helicopters'] in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] not in [4, 5, 6] and pos_unit[helicopters] in [4, 5, 6]')
            if pos_unit['helicopters'] == 4:
                if DEBUG:
                    print('heli 4')
                if pos_unit['fighter'] in [2, 3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [8, 9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['fighter'] in [1]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [7]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 5:
                if DEBUG:
                    print('heli 5')
                if pos_unit['fighter'] in [1, 3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [7, 9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['fighter'] in [2]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [8]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 6:
                if DEBUG:
                    print('heli 6')
                if pos_unit['fighter'] in [1, 2]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [7, 8]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['fighter'] in [3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['fighter'] in [9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=FIGHTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=62)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
        if pos_unit['fighter']in [4, 5, 6] and pos_unit['helicopters'] not in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] in [4, 5, 6] and pos_unit[helicopters] not in [4, 5, 6]')
            if pos_unit['fighter'] == 4:
                if DEBUG:
                    print('fighter 4')
                if pos_unit['helicopters'] in [2, 3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [8, 9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['helicopters'] in [1]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [7]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['fighter'] == 5:
                if DEBUG:
                    print('fighter 5')
                if pos_unit['helicopters'] in [1, 3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [7, 9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['helicopters'] in [2]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [8]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['fighter'] == 6:
                if DEBUG:
                    print('fighter 6')
                if pos_unit['helicopters'] in [1, 2]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [7, 8]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                if pos_unit['helicopters'] in [3]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                if pos_unit['helicopters'] in [9]:
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=HELICOPTER_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=100)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)

        if pos_unit['fighter'] not in [4, 5, 6] and pos_unit['helicopters'] not in [4, 5, 6]:
            if DEBUG:
                print('FLY: pos_unit[fighter] not in [4, 5, 6] and pos_unit[helicopters] not in [4, 5, 6]')
            if pos_unit['fighter'] in [1, 2, 3] and pos_unit['helicopters'] in [1, 2, 3]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] in [7, 8, 9] and pos_unit['helicopters'] in [7, 8, 9]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['fighter'] == 1 and pos_unit['helicopters'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] == 1 and pos_unit['helicopters'] in [8, 9]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] == 2 and pos_unit['helicopters'] in [7, 9]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] == 3 and pos_unit['helicopters'] in [7, 8]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] == 2 and pos_unit['helicopters'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            elif pos_unit['fighter'] == 3 and pos_unit['helicopters'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)

            elif pos_unit['helicopters'] == 1 and pos_unit['fighter'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 1 and pos_unit['fighter'] in [8, 9]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 2 and pos_unit['fighter'] in [7, 9]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 3 and pos_unit['fighter'] in [7, 8]:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 2 and pos_unit['fighter'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            elif pos_unit['helicopters'] == 3 and pos_unit['fighter'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=HELICOPTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=FIGHTER_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=90)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)

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
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 4 and pos_unit['ifv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            if ifv_pos[0] == 5 and pos_unit['ifv'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 5 and pos_unit['ifv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            if ifv_pos[0] == 6 and pos_unit['ifv'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if ifv_pos[0] == 6 and pos_unit['ifv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=IFV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

        # arrv location (if 2 in middle)
        if (pos_unit['arrv'] not in [4, 5, 6]) and (pos_unit['ifv'] in [4, 5, 6]) and (pos_unit['tank'] in [4, 5, 6]):
            arrv_pos = [4, 5, 6]
            arrv_pos.remove(pos_unit['ifv'])
            arrv_pos.remove(pos_unit['tank'])
            if DEBUG:
                print('2 in of middle / ARRV', arrv_pos)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 4 and pos_unit['arrv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            if arrv_pos[0] == 5 and pos_unit['arrv'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 5 and pos_unit['arrv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

            if arrv_pos[0] == 6 and pos_unit['arrv'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=450)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
            if arrv_pos[0] == 6 and pos_unit['arrv'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=ARRV_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)

        # tank location (if 2 in middle)
        if (pos_unit['tank'] not in [4, 5, 6]) and (pos_unit['ifv'] in [4, 5, 6]) and (pos_unit['arrv'] in [4, 5, 6]):
            tank_pos = [4, 5, 6]
            tank_pos.remove(pos_unit['ifv'])
            tank_pos.remove(pos_unit['arrv'])
            if DEBUG:
                print('2 in of middle / TANK', tank_pos)
            if tank_pos[0] == 4 and pos_unit['tank'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=550)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 4 and pos_unit['tank'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=550)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)

            if tank_pos[0] == 5 and pos_unit['tank'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 5 and pos_unit['tank'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)

            if tank_pos[0] == 6 and pos_unit['tank'] == 1:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=550)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 7:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=550)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 2:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 8:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 3:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
            if tank_pos[0] == 6 and pos_unit['tank'] == 9:
                self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                            bottom=self.world.height, group=TANK_GROUP)
                self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)

        # all 3 not in middle
        if (pos_unit['tank'] in [1, 2, 3]) and (pos_unit['ifv'] in [1, 2, 3]) and (pos_unit['arrv'] in [1, 2, 3]):
            if DEBUG:
                print('3 not in middle 123')
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=TANK_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=IFV_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74)
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=ARRV_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)

        elif (pos_unit['tank'] in [7, 8, 9]) and (pos_unit['ifv'] in [7, 8, 9]) and (pos_unit['arrv'] in [7, 8, 9]):
            if DEBUG:
                print('3 not in middle 789')
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=TANK_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=IFV_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74)
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                        bottom=self.world.height, group=ARRV_GROUP)
            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
        elif (pos_unit['tank'] in [1, 2, 3, 7, 8, 9]) and (pos_unit['ifv'] in [1, 2, 3, 7, 8, 9]) and (pos_unit['arrv'] in [1, 2, 3, 7, 8, 9]):
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
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=TANK_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                if group_inside == 'arrv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                if group_inside == 'ifv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, group=IFV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                occupyed_places.append(4)
            if 2 in vehicle_places:
                if DEBUG:
                    print('2')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 2:
                        group_inside = key
                if group_inside == 'tank':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=TANK_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                if group_inside == 'arrv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                if group_inside == 'ifv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=IFV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                occupyed_places.append(5)
            if 3 in vehicle_places:
                if DEBUG:
                    print('3')
                group_inside = ''
                for key in ['tank', 'arrv', 'ifv']:
                    if pos_unit[key] == 3:
                        group_inside = key
                if group_inside == 'tank':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=TANK_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                if group_inside == 'arrv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=ARRV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                if group_inside == 'ifv':
                    self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                bottom=self.world.height, group=IFV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
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
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    occupyed_places.append(5)
                else:
                    if 4 not in occupyed_places and 7 not in vehicle_places:
                        if group_inside == 'tank':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=TANK_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                        if group_inside == 'arrv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=ARRV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                        if group_inside == 'ifv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=IFV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                        occupyed_places.append(5)
                    elif 4 not in occupyed_places and 9 not in vehicle_places:
                        if group_inside == 'tank':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=TANK_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                        if group_inside == 'arrv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=ARRV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                        if group_inside == 'ifv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=IFV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                        occupyed_places.append(5)
                    elif 6 not in occupyed_places:
                        if group_inside == 'tank':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=TANK_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                        if group_inside == 'arrv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=ARRV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                        if group_inside == 'ifv':
                            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                        bottom=self.world.height, group=IFV_GROUP)
                            self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                            self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
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
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    occupyed_places.append(5)
                elif 6 not in occupyed_places:
                    if group_inside == 'tank':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=600)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=310)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=480)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=148, y=0, next_delay=480)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
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
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    occupyed_places.append(4)
                elif 5 not in occupyed_places:
                    if group_inside == 'tank':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    occupyed_places.append(5)
                elif 4 not in occupyed_places:
                    if group_inside == 'tank':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=600)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=300)
                    if group_inside == 'arrv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=480)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
                    if group_inside == 'ifv':
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=-148, y=0, next_delay=480)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-74, next_delay=230)
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
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                elif 1 in pos_units_ground.values() and 3 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 3 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                    if pos_unit['tank'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                    if pos_unit['arrv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                    if pos_unit['ifv'] == 3:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                    self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                elif 1 in pos_units_ground.values() and 7 in pos_units_ground.values():
                    if DEBUG:
                        print('1 in pos_units_ground and 7 in pos_units_ground')
                    if pos_unit['tank'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=TANK_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
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
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
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
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=300)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=300)
                    if pos_unit['arrv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=ARRV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
                        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=74, next_delay=230)
                    if pos_unit['ifv'] == 1:
                        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                                    bottom=self.world.height, group=IFV_GROUP)
                        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=230)
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

        """ move all units in geometry """
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=96, next_delay=50)

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=96)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-68, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=98, right=1024, bottom=102)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-54, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=102, right=1024, bottom=106)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-40, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=106, right=1024, bottom=110)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-28, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=110, right=1024, bottom=120)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-14, next_delay=16)

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=144, right=1024, bottom=146)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=54, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=138, right=1024, bottom=143)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=40, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=132, right=1024, bottom=137)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=28, next_delay=16)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=126, right=1024, bottom=131)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=14, next_delay=150)

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=72, bottom=1024)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=-5, next_delay=32)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=150, top=0, right=1024, bottom=1024)
        self._add_command_to_orders(action=ActionType.MOVE, x=0, y=5, next_delay=32)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=72, bottom=1024)
        self._add_command_to_orders(action=ActionType.MOVE, x=74, y=0, next_delay=10)
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=150, top=0, right=1024, bottom=1024)
        self._add_command_to_orders(action=ActionType.MOVE, x=-74, y=0, next_delay=300)

        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, left=0, top=0, right=1024, bottom=1024)
        self._add_command_to_orders(action=ActionType.SCALE, x=119, y=119, factor=0.2, next_delay=120)
        self._add_command_to_orders(action=ActionType.ROTATE, x=119, y=119, angle=0.9, next_delay=200)

    def state_whirlwind(self):
        if len(self.orders) == 0:
            self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=1024, bottom=1024)
            self._add_command_to_orders(action=ActionType.SCALE, factor=0.1, next_delay=40)
            self._add_command_to_orders(action=ActionType.MOVE, max_speed=0.2, next_delay=60)

    def big_boom(self):
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

        self.current_order_wait = 0
        self._add_command_to_orders(action=ActionType.CLEAR_AND_SELECT, right=self.world.width,
                                    bottom=self.world.height, priority=True)
        self._add_command_to_orders(action=ActionType.SCALE, x=attack_x, y=attack_y,
                                    factor=10, priority=True, next_delay=ticks_before)

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
        if vehicle_type is not None:
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
            vehicle_id, min_distance, vision = self._get_closest_to_enemy_vehicle()
            if vehicle_id == -1:
                return False
            if min_distance < 10:
                return False
            if min_distance < vision - 15:
                if DEBUG:
                    print('NUCLEAR 1', vehicle_id, min_distance, vision)
                self.nuclear_x = self.enemy_center[0]
                self.nuclear_y = self.enemy_center[1]
                self.vehicle_id_nuclear = vehicle_id
            elif min_distance <= vision + 10:
                if DEBUG:
                    print('NUCLEAR 2', vehicle_id, min_distance, vision)
                delta = min_distance / vision
                self.nuclear_x = self.my_vehicles[vehicle_id].x + (self.enemy_center[0] - self.my_vehicles[vehicle_id].x) / delta
                self.nuclear_y = self.my_vehicles[vehicle_id].y + (self.enemy_center[1] - self.my_vehicles[vehicle_id].y) / delta
                self.vehicle_id_nuclear = vehicle_id
                return True
        return False

    def _get_closest_to_enemy_vehicle(self):
        min_distance, best_id = 100000000, -1
        min_distance_flight, best_id_flight = 100000000, -1
        for vehicle in self.my_vehicles.values():
            distance = (vehicle.x - self.enemy_center[0]) ** 2 + (vehicle.y - self.enemy_center[1]) ** 2
            if self.my_initial_vehicles[vehicle.id].type == VehicleType.FIGHTER:
                if min_distance_flight > distance:
                    min_distance_flight = distance
                    best_id_flight = vehicle.id
            else:
                if min_distance > distance:
                    min_distance = distance
                    best_id = vehicle.id

        if best_id_flight > 0:
            if min_distance_flight < min_distance + 40:
                return best_id_flight, math.sqrt(min_distance_flight), self.my_initial_vehicles[best_id].vision_range
        if best_id == -1:
            return best_id, math.sqrt(min_distance), 0
        return best_id, math.sqrt(min_distance), self.my_initial_vehicles[best_id].vision_range

    def _nuclear_defence(self):
        if self.me.next_nuclear_strike_tick_index == -1:
            return False
        if self.me.next_nuclear_strike_vehicle_id in self.my_vehicles.keys():
            return False
        return True


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
                    world.tick_index, self.commands_executed, self.my_bot.state, ACTIONS[bot_answer.action], bot_answer.group, bot_answer.vehicle_id))
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















