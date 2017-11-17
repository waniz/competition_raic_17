import copy
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

""" Tuning params """
NUCLEAR_DISTANCE = [100, 300]


class MyStrategy:
    random = None
    terrain, weather = None, None
    orders = deque(maxlen=4000)
    next_wait = 0
    mean_my_x, mean_my_y = 0, 0
    enemy_vehicles = {}
    my_vehicles = {}

    def game_init(self, world, game, move, me):
        """ Init game, fill orders deque for regrouping """
        if not self.random:
            self.random = game.random_seed
        self.terrain = world.terrain_by_cell_x_y
        self.weather = world.weather_by_cell_x_y

        if DEBUG:
            print('[DEBUG] ---- ACTIVE ---- ')
            print('Active actions: %s' % game.base_action_count)
            print('My Game ID: %s' % me.id)

        for vehicle in world.new_vehicles:
            if vehicle.player_id == me.id:
                self.my_vehicles[vehicle.id] = vehicle
            else:
                self.enemy_vehicles[vehicle.id] = vehicle

        self.mean_my_x = sum([vehicle.x for vehicle in self.my_vehicles.values()]) / len(list(self.my_vehicles.values()))
        self.mean_my_y = sum([vehicle.y for vehicle in self.my_vehicles.values()]) / len(list(self.my_vehicles.values()))

        if DEBUG:
            print(self.mean_my_x, self.mean_my_y)
            print(len(list(self.my_vehicles.values())))
            print(len(list(self.enemy_vehicles.values())))

        mover = copy.deepcopy(move)
        mover.action = ActionType.CLEAR_AND_SELECT
        mover.right = world.width
        mover.bottom = world.height
        self.orders.append(mover)

        mover = copy.deepcopy(move)
        mover.action = ActionType.SCALE
        mover.factor = 1
        mover.x = self.mean_my_x
        mover.y = self.mean_my_y
        self.orders.append(mover)

        self.orders.append('wait 80')

        mover = copy.deepcopy(move)
        mover.action = ActionType.ROTATE
        mover.angle = 1.5
        mover.x = self.mean_my_x
        mover.y = self.mean_my_y
        self.orders.append(mover)

        self.orders.append('wait 120')

        mover = copy.deepcopy(move)
        mover.action = ActionType.ROTATE
        mover.angle = 1
        mover.x = self.mean_my_x
        mover.y = self.mean_my_y
        self.orders.append(mover)

        self.orders.append('wait 100')

        mover = copy.deepcopy(move)
        mover.action = ActionType.SCALE
        mover.factor = 0.3
        mover.x = self.mean_my_x
        mover.y = self.mean_my_y
        self.orders.append(mover)
        self.orders.append('wait 20')

        for _ in range(100):

            mover = copy.deepcopy(move)
            mover.action = ActionType.ROTATE
            mover.angle = 1
            mover.x = self.mean_my_x
            mover.y = self.mean_my_y
            self.orders.append(mover)
            self.orders.append('wait 60')

            mover = copy.deepcopy(move)
            mover.action = ActionType.SCALE
            mover.factor = 0.1
            mover.x = self.mean_my_x
            mover.y = self.mean_my_y
            self.orders.append(mover)
            self.orders.append('wait 60')

            mover = copy.deepcopy(move)
            mover.action = ActionType.CLEAR_AND_SELECT
            mover.right = world.width
            mover.bottom = world.height
            self.orders.append(mover)

            mover = copy.deepcopy(move)
            mover.action = ActionType.MOVE
            mover.x = 990
            mover.y = 990
            mover.max_speed = 0.3
            self.orders.append(mover)
            self.orders.append('wait 25')
        pass

    def tick_init(self, world, game, me):
        """ find out all my armies and types """

        for vehicle in world.vehicle_updates:
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

        if self.next_wait > 0:
            self.next_wait -= 1
            return None
        if len(self.orders) > 0:
            command = self.orders.popleft()
            if type(command) is not str:
                return command
            else:
                self.next_wait += int(command.split(' ')[1])
        return None

    def move(self, me: Player, world: World, game: Game, move: Move):
        """ main method """

        if world.tick_index == 0:
            self.game_init(world=world, game=game, move=move, me=me)
        move_it = self.tick_init(world, game, me)

        if move_it:

            move.action = move_it.action
            move.right = move_it.right
            move.bottom = move_it.bottom
            if move.action != 7:
                self.mean_my_x = sum([vehicle.x for vehicle in self.my_vehicles.values()]) / len(
                    list(self.my_vehicles.values()))
                self.mean_my_y = sum([vehicle.y for vehicle in self.my_vehicles.values()]) / len(
                    list(self.my_vehicles.values()))
                if DEBUG:
                    print(self.mean_my_x, self.mean_my_y)
                move.x = self.mean_my_x
                move.y = self.mean_my_y
            else:
                move.x = move_it.x
                move.y = move_it.y
            move.factor = move_it.factor
            move.max_speed = move_it.max_speed
            move.angle = move_it.angle

        else:
            move = None














