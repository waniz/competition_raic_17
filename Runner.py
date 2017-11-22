import sys

from MyStrategy import MyStrategy
from RemoteProcessClient import RemoteProcessClient
from model.Move import Move


class Runner:
    def __init__(self):
        if sys.argv.__len__() == 4:
            self.remote_process_client = RemoteProcessClient(sys.argv[1], int(sys.argv[2]))
            self.token = sys.argv[3]
        else:
            self.remote_process_client = RemoteProcessClient("127.0.0.1", 31001)
            self.token = "0000000000000000"

    def run(self):
        try:
            self.remote_process_client.write_token_message(self.token)
            self.remote_process_client.write_protocol_version_message()
            self.remote_process_client.read_team_size_message()
            game = self.remote_process_client.read_game_context_message()

            strategy = MyStrategy()

            while True:
                player_context = self.remote_process_client.read_player_context_message()
                if player_context is None:
                    break

                player = player_context.player
                if player is None:
                    break

                move = Move()
                strategy.move(player, player_context.world, game, move)

                # if move.action:
                #     print('[Tick %s] ACTION:%s, GROUP:%s TYPE:%s RIGHT:%s BOTTOM:%s X:%s Y:%s' % (
                #         player_context.world.tick_index, move.action, move.group, move.vehicle_type, move.right, move.bottom, move.x, move.y))

                self.remote_process_client.write_move_message(move)
        finally:
            self.remote_process_client.close()


Runner().run()
