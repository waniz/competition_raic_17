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


class MyStrategy:
    random = None
    terrain, weather = None, None
    STATE = None
    orders = deque(maxlen=1000)
    is_init_regroup = False

    def move(self, me: Player, world: World, game: Game, move: Move):
        """ main method """

        if world.tick_index == 0:
            move.action = ActionType.CLEAR_AND_SELECT
            move.right = world.width
            move.bottom = world.height
        if world.tick_index == 1:
            move.action = ActionType.MOVE
            move.x = world.width / 2.0
            move.y = world.height / 2.0