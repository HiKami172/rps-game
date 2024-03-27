"""RPS game"""

from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass, field

from bot import RPSBot


class RPSMove(Enum):
    """

    :class:`RPSMove` is an enumeration class that represents moves in
    the game of Rock-Paper-Scissors.

    Attributes:
        ROCK: Represents the move "Rock" with value "R".
        PAPER: Represents the move "Paper" with value "P".
        SCISSORS: Represents the move "Scissors" with value "S".
        NONE: Represents no move with value "".
    """

    ROCK: str = "R"
    PAPER: str = "P"
    SCISSORS: str = "S"
    NONE: str = ""


class GameStatus(Enum):
    """
    Represents the status of a game.

    This class is an enumeration that defines the possible status values of a game.

    Attributes:
        PENDING: Represents the status when the game is pending.
        WIN: Represents the status when the game is won.
        LOSS: Represents the status when the game is lost.
        DRAW: Represents the status when the game is a draw.

    """

    PENDING: str = "PENDING"
    WIN: str = "WIN"
    LOSS: str = "LOSS"
    DRAW: str = "DRAW"


class RoundResult(Enum):
    """
    The RoundResult class is an enumeration that represents the possible results
    of a round in a game.

    Attributes:
        WIN: Represents a round result of "WIN".
        LOSS: Represents a round result of "LOSS".
        TIE: Represents a round result of "TIE".
        NONE: Represents a round result of "NONE".
    """

    WIN: str = "WIN"
    LOSS: str = "LOSS"
    TIE: str = "TIE"
    NONE: str = "NONE"


def get_move_result(player_move: RPSMove, bot_move: RPSMove) -> RoundResult:
    """
    This method takes in the player's move and the bot's move and determines
    the result of the round based on the Rock-Paper-Scissors game rules.


    :param player_move: The move made by the player. It should be an instance of
     the RPSMove enumeration.
    :param bot_move: The move made by the bot. It should be an instance of the RPSMove enumeration.
    :return: The result of the round. It should be an instance of the RoundResult enumeration.

    """
    if player_move == bot_move:
        return RoundResult.TIE
    if (
        (player_move == RPSMove.ROCK and bot_move == RPSMove.SCISSORS)
        or (player_move == RPSMove.PAPER and bot_move == RPSMove.ROCK)
        or (player_move == RPSMove.SCISSORS and bot_move == RPSMove.PAPER)
    ):
        return RoundResult.WIN
    return RoundResult.LOSS


@dataclass
class GameState:
    """
    Represents the state of the game.

    Attributes:
        player_score: The score of the player.
        bot_score: The score of the bot.
        turn: The current turn number.
        history: The list of tuples representing the moves and results of each round.
        status: The status of the game.
    """

    player_score: int = field(default=0)
    bot_score: int = field(default=0)
    turn: int = field(default=1)
    history: List[Tuple[RPSMove, RPSMove, RoundResult]] = field(default_factory=list)
    status: GameStatus = field(default=GameStatus.PENDING)

    def update_score(self, round_result: RoundResult) -> None:
        """
        Update the scores based on the result of a round.

        :param round_result: The result of the round (win, loss, or draw).
        :type round_result: RoundResult
        :return: None
        """
        if round_result == RoundResult.WIN:
            self.player_score += 1
            self.bot_score = max(0, self.bot_score - 1)
        elif round_result == RoundResult.LOSS:
            self.player_score = max(0, self.player_score - 1)
            self.bot_score += 1
        self.turn += 1

    def add_to_history(
        self, player_move: RPSMove, bot_move: RPSMove, round_result: RoundResult
    ) -> None:
        """Add round to the history."""
        self.history.append((player_move, bot_move, round_result))

    def get_last_round(self) -> Tuple[RPSMove, RPSMove, RoundResult]:
        """
        Returns the data of the last round.
        :return: player_move, bot_move, round_result
        """
        return self.history[-1]

    def is_finished(self) -> bool:
        """Checks if the game is finished without changing the game state."""
        return self.turn == 30 or self.player_score == 10 or self.bot_score == 10

    def update_status(self) -> None:
        """Changes the game state if the game is finished."""
        if self.turn == 30:
            if self.player_score > self.bot_score:
                self.status = GameStatus.WIN
            elif self.player_score < self.bot_score:
                self.status = GameStatus.LOSS
            else:
                self.status = GameStatus.DRAW
        elif self.player_score == 10:
            self.status = GameStatus.WIN
        elif self.bot_score == 10:
            self.status = GameStatus.LOSS


class RPSGame:
    """
    Rock-Paper-Scissors game main class.
    Initializes the game initial state and a bot to play with.
    """

    def __init__(self):
        self.bot = RPSBot()
        self.state = GameState()

    def restart_game(self) -> None:
        """Resets the game and bot states."""
        self.state = GameState()
        self.bot.reset_state()

    def calculate_bot_move(self, player_move: RPSMove) -> RPSMove:
        """Calculates the next move of the bot and updates its weights."""
        bot_move = RPSMove(self.bot.predict())
        self.bot.update_transitions(player_move.value)
        return bot_move

    def move(self, player_move: RPSMove) -> GameState:
        """Get player's move and return the new state of the game."""
        bot_move = self.calculate_bot_move(player_move)
        round_result = get_move_result(player_move, bot_move)
        self.state.update_score(round_result)
        self.state.add_to_history(player_move, bot_move, round_result)

        if self.state.is_finished():
            self.bot.save_weights()
            self.state.update_status()

        return self.state
