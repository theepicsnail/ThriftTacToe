namespace py ttt

enum Player {
  X, O
}

enum Position {
  // [T]op, [M]iddle, [B]ottom
  // [L]eft, [C]enter, [R]ight
  TL, TC, TR,
  ML, MC, MR,
  BL, BC, BR,
}

struct MoveRequest {
  1: string game_id,
  2: string move_key,
  3: Position position
}

enum MoveReplyStatus {
  ACCEPTED,
  NOT_YOUR_TURN,
  POSITION_TAKEN,
  INVALID_KEY,
  INVALID_GAME,
}

struct JoinReply {
  // The player that was joined by the JoinGame request
  // This will be your player, or empty if the join failed
  1: optional Player player

  // If the player joined, move_key contains a secret key that
  // is required to move on behalf of your player.
  // This prevents the other player from making your move.
  2: optional string move_key
}

enum GameState {
  NONEXISTENT,
  INITIALIZING,
  WAITING_X,
  WAITING_O,
  X_WON,
  O_WON,
  TIE
}

service TTTService {
  //Create a new game, get the game Id
  string NewGame(), 

  //Attempt to join the game with the game id game_id
  JoinReply JoinGame(1:string game_id) 
  
  //Attempt to make a move
  MoveReplyStatus Move(1:MoveRequest req)

  string GetBoard(1:string game_id)

  GameState GetState(1:string game_id)
}
