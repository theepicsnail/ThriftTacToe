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

input_to_pos = {
    "1":Position.BL,
    "2":Position.BC,
    "3":Position.BR,
    "4":Position.ML,
    "5":Position.MC,
    "6":Position.MR,
    "7":Position.TL,
    "8":Position.TC,
    "9":Position.TR}
try:
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)

    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = TTTService.Client(protocol)

    transport.open()
    
    game_id = ""
    move_key = ""
    my_player = None

    #Get a game id, from parameters, or from making a new game
    if len(sys.argv) == 1:
        print "Creating new game"
        game_id = client.NewGame()
        print "Created game:", game_id
    else:
        game_id = sys.argv[1]

    #attempt to join that game
    print "Joining game", game_id
    join_reply = client.JoinGame(game_id)
    if join_reply.move_key:
        move_key = join_reply.move_key
        my_player = join_reply.player
        print "Joined."
    else:
        print "Failed to join"
        print join_reply
        sys.exit(1)

    import time
    while True:
        state = client.GetState(game_id)
        if (state==GameState.WAITING_X and my_player == Player.X) or \
            (state==GameState.WAITING_O and my_player == Player.O):
            #my turn
            print client.GetBoard(game_id)
            pos = raw_input(">")
            while pos not in input_to_pos:
                print "Invalid input."
                pos = raw_input(">")
            pos = input_to_pos[pos]
            req = MoveRequest()
            req.game_id = game_id
            req.move_key = move_key
            req.position = pos
            rep = client.Move(req)
            print MoveReplyStatus._VALUES_TO_NAMES[rep]
            if rep == MoveReplyStatus.ACCEPTED:
                print client.GetBoard(game_id)
                print "Waiting on other player"
        elif state in [GameState.X_WON, GameState.O_WON, GameState.TIE]:
            print "Game over"
            print GameState._VALUES_TO_NAMES[state]
            break
        elif state == GameState.INITIALIZING:
            print "Waiting for other player to join"
            time.sleep(1)
        elif state == GameState.NONEXISTENT:
            print "Invalid game id"
            break
        else:
            time.sleep(1)
    transport.close()
except Thrift.TException, tx:
    print tx
