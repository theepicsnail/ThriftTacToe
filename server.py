import sys
import os
if not os.path.exists("gen-py"):
    print "gen-py does not exist. Have you run build.sh?"
    sys.exit(1)
sys.path.append("gen-py")


from ttt import TTTService
from ttt.ttypes import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import uuid

WINNING_PLACEMENTS = [
    [Position.TL, Position.TC, Position.TR],
    [Position.TL, Position.MC, Position.BR],
    [Position.TL, Position.ML, Position.BL],
    [Position.TC, Position.MC, Position.BC],
    [Position.TR, Position.MR, Position.BR],
    [Position.ML, Position.MC, Position.MR],
    [Position.BL, Position.MC, Position.TR],
    [Position.BL, Position.BC, Position.BR],
]
class Game:
    def __init__(self):
        self.x_key = None
        self.o_key = None
        self.state = GameState.INITIALIZING
        self.board = {}
    def draw_board(self):
        out = ""
        def getCh(pos):
            v = self.board.get(pos, None)
            if v is None:
                return " "
            return Player._VALUES_TO_NAMES[v]

        out += getCh(Position.TL)
        out += "|"
        out += getCh(Position.TC)
        out += "|"
        out += getCh(Position.TR)
        out += "\n-+-+-\n"
        out += getCh(Position.ML)
        out += "|"
        out += getCh(Position.MC)
        out += "|"
        out += getCh(Position.MR)
        out += "\n-+-+-\n"
        out += getCh(Position.BL)
        out += "|"
        out += getCh(Position.BC)
        out += "|"
        out += getCh(Position.BR)
        return out
    def joinable(self):
        return self.state == GameState.INITIALIZING
    
    def join(self):
        if self.x_key == None:
            print "X joined"
            self.x_key = str(uuid.uuid4())
            return Player.X, self.x_key
        elif self.o_key == None:
            print "O joined"
            self.state = GameState.WAITING_X
            self.o_key = str(uuid.uuid4())
            return Player.O, self.o_key
        return None, None
    
    def move(self, player_key, position):
        if player_key == self.x_key:
            if self.state != GameState.WAITING_X:
                return MoveReplyStatus.NOT_YOUR_TURN
            return self._perform_move(Player.X, position)
        elif player_key == self.o_key:
            if self.state != GameState.WAITING_O:
                return MoveReplyStatus.NOT_YOUR_TURN
            return self._perform_move(Player.O, position)
        return MoveReplyStatus.INVALID_KEY

    def _perform_move(self, player, position):
        if position in self.board:
            return MoveReplyStatus.POSITION_TAKEN

        if self.state == GameState.WAITING_X:
            self.state = GameState.WAITING_O
        elif self.state == GameState.WAITING_O:
            self.state = GameState.WAITING_X
        else:
            #This should be filtered out by move(key,pos)
            return MoveReplyStatus.NOT_YOUR_TURN

        self.board[position] = player
        self._check_for_win()
        return MoveReplyStatus.ACCEPTED

    def _check_for_win(self):
        for placement in WINNING_PLACEMENTS:
            first = self.board.get(placement[0], None)
            if first is None:
                continue
            second = self.board.get(placement[1], None)
            if second != first:
                continue
            last = self.board.get(placement[2], None)
            if first != last:
                continue

            if first == Player.X:
                self.state = GameState.X_WON
                return
            elif first == Player.O:
                self.state = GameState.O_WIN
                return

        if len(self.board) == 9:
            self.state = GameState.TIE

class TTTServer:
    games = {}

    def NewGame(self):
        gid = str(uuid.uuid4())    
        g = Game()
        self.games[gid] = g
        return gid

    def JoinGame(self, game_id):
        print "Join", game_id
        print self.games
        if game_id not in self.games:
            return JoinReply() # Empty reply.

        game = self.games[game_id]
        if not game.joinable():
            return JoinReply()

        player, key = game.join()
        reply = JoinReply()
        reply.player = player
        reply.move_key = key
        return reply

    def Move(self, req):
        if req.game_id not in self.games:
            return MoveReplyStatus.INVALID_GAME
        game = self.games[req.game_id]
        return game.move(req.move_key, req.position)

    def GetState(self, game_id):
        if game_id not in self.games:
            return GameState.NONEXISTENT
        return self.games[game_id].state

    def GetBoard(self, game_id):
        if game_id not in self.games:
            return ""
        return self.games[game_id].draw_board()
if __name__=="__main__":
    handler = TTTServer()
    processor = TTTService.Processor(handler)

    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.serve()
