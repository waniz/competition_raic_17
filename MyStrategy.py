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


class MyStrategy:
    random = None
    terrain, weather = None, None
    STATE = None
    orders = deque(maxlen=1000)
    is_init_regroup = False
    next_wait = 0

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
        new_vehicles = world.new_vehicles

        # get my units and formation in 2D-space
        my_vehicles = [x for x in new_vehicles if x.player_id == me.id]
        mean_all_x = sum([my_vehicle.x for my_vehicle in my_vehicles]) / len(my_vehicles)
        mean_all_y = sum([my_vehicle.x for my_vehicle in my_vehicles]) / len(my_vehicles)

        if DEBUG:
            print(mean_all_x, mean_all_y)

        mover = copy.deepcopy(move)
        mover.action = ActionType.CLEAR_AND_SELECT
        mover.right = world.width
        mover.bottom = world.height
        self.orders.append(mover)

        mover = copy.deepcopy(move)
        mover.action = ActionType.SCALE
        mover.factor = 1
        mover.x = mean_all_x
        mover.y = mean_all_y
        self.orders.append(mover)

        self.orders.append('wait 60')

        mover = copy.deepcopy(move)
        mover.action = ActionType.ROTATE
        mover.angle = 1.5
        mover.x = mean_all_x
        mover.y = mean_all_y
        self.orders.append(mover)

        self.orders.append('wait 120')

        mover = copy.deepcopy(move)
        mover.action = ActionType.ROTATE
        mover.angle = 1
        mover.x = mean_all_x
        mover.y = mean_all_y
        self.orders.append(mover)

        self.orders.append('wait 100')

        mover = copy.deepcopy(move)
        mover.action = ActionType.SCALE
        mover.factor = 0.3
        mover.x = mean_all_x
        mover.y = mean_all_y
        self.orders.append(mover)
        self.orders.append('wait 20')

        for _ in range(100):
            mean_all_x += 15
            mean_all_y += 15
            mover = copy.deepcopy(move)
            mover.action = ActionType.ROTATE
            mover.angle = 1
            mover.x = mean_all_x
            mover.y = mean_all_y
            self.orders.append(mover)
            self.orders.append('wait 60')

            mover = copy.deepcopy(move)
            mover.action = ActionType.SCALE
            mover.factor = 0.1
            mover.x = mean_all_x
            mover.y = mean_all_y
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
            mover.factor = 0.3
            self.orders.append(mover)
            self.orders.append('wait 10')
        pass

    def tick_init(self, world, game, me):
        """ find out all my armies and types """
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
            if DEBUG:
                print('Receiver action', move_it.action)
            move.action = move_it.action
            move.right = move_it.right
            move.bottom = move_it.bottom
            move.x = move_it.x
            move.y = move_it.y
            move.factor = move_it.factor
            move.max_speed = move_it.max_speed
            move.angle = move_it.angle

        else:
            move = None














