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


class DecisionMaker:
    def __init__(self):
        pass

    def get_state(self):
        pass


class MyStrategy:
    random = None
    terrain, weather = None, None

    def game_init(self, world, game):
        if not self.random:
            self.random = game.random_seed
        self.terrain = world.terrain_by_cell_x_y
        self.weather = world.weather_by_cell_x_y

    def tick_init(self, world, game, me):
        pass

    def move(self, me: Player, world: World, game: Game, move: Move):

        if world.tick_index == 0:
            self.game_init(world=world, game=game)
        self.tick_init(world, game, me)

        if me.remaining_action_cooldown_ticks > 0:
            return











