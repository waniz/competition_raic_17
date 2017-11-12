from collections import deque
import copy

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


class MyStrategy:
    random = None
    terrain, weather = None, None
    STATE = None
    regroup_orders = deque(maxlen=1000)
    is_init_regroup = False

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
        



    def tick_init(self, world, game, me):
        """ find out all my armies and types """
        if len(self.regroup_orders) > 0:
            return self.regroup_orders.popleft()
        new_vehicles = world.vehicle_updates
        print(len(new_vehicles))

    def move(self, me: Player, world: World, game: Game, move: Move):
        """ main method """

        if world.tick_index == 0:
            self.game_init(world=world, game=game, move=move, me=me)
        temp_move = self.tick_init(world, game, me)

        if world.tick_index < 2000:
            self.STATE = 'init_regroup'

        if DEBUG:
            print('[STATE] %s' % self.STATE)

        if world.tick_index == 0:
            move.action = ActionType.CLEAR_AND_SELECT
            move.right = world.width
            move.bottom = world.height
        if world.tick_index == 1:
            move.action = ActionType.MOVE
            move.x = world.width / 2.0
            move.y = world.height / 2.0

        if me.remaining_action_cooldown_ticks > 0:
            return
        else:
            move = temp_move
            print(move)

    def _fill_commands_for_regroup(self, world, move):
        """ fill regroup deque """

        pass

        # mover = copy.deepcopy(move)
        # mover.action = ActionType.CLEAR_AND_SELECT
        # mover.right = world.width
        # mover.bottom = world.height
        # self.regroup_orders.append(mover)
        #
        # mover = copy.deepcopy(move)
        # mover.action = ActionType.MOVE
        # mover.x = world.width / 2.0
        # mover.y = world.height / 2.0
        # self.regroup_orders.append(mover)

















