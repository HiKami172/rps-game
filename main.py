"""
Flet based Rock, Paper, Scissors GUI.
"""
from typing import Optional, Callable

import flet as ft  # type: ignore
from game import RPSGame, RPSMove, GameState, GameStatus, RoundResult

ROCK_IMAGE = "assets/rock.png"
PAPER_IMAGE = "assets/paper.png"
SCISSORS_IMAGE = "assets/scissors.png"

BOT_IMAGE = "assets/bot.png"
PLAYER_IMAGE = "assets/player.png"
BACKGROUND_IMAGE = "assets/background.jpg"


class MoveButton(ft.Container):
    """
    Rock-Paper-Scissors game move control.
    """
    bg_color = "white"

    def __init__(self, on_click: Callable, image_url: Optional[str] = None, bg_color="white"):
        self.bg_color = bg_color
        super().__init__(
            width=100,
            height=100,
            margin=ft.margin.symmetric(horizontal=20),
            bgcolor=self.bg_color,
            border_radius=5,
            border=ft.border.all(0.5, "white"),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15),
            content=ft.Container(
                margin=10,
                image_src=image_url,
                alignment=ft.alignment.center
            ),
            on_click=on_click,
            on_hover=self.handle_hover
        )

    def handle_hover(self, e) -> None:
        """
        on_hover event handler.
        Changes control's opacity.
        :param e: event data.
        :return: None
        """
        self.opacity = 0.8 if e.data == "true" else 1
        self.update()


class PlayerScreen(ft.Container):
    """
    Player screen container control.
    Stores the image of the player and displays his moves.
    """

    def __init__(self, default_image_src: str):
        self.default_image_src = default_image_src
        self.image_container = ft.Container(
            margin=40,
            image_src=self.default_image_src,
            image_fit=ft.ImageFit.FILL,
            alignment=ft.alignment.center
        )
        self.set_move_image()
        super().__init__(
            width=300,
            height=300,
            margin=ft.margin.symmetric(horizontal=30),
            border_radius=10,
            bgcolor="grey",
            opacity=0.9,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                blur_style=ft.ShadowBlurStyle.OUTER,
            ),
            content=self.image_container
        )

    def set_move_image(self, move: Optional[RPSMove] = None) -> None:
        """
        Sets the move image to the player's screen.
        :param move: The move to set
        :return: None
        """
        if not move:
            self.image_container.image_src = self.default_image_src
            self.image_container.image_opacity = 0.4
            return
        self.image_container.image_opacity = 1
        match move:
            case RPSMove.ROCK:
                self.image_container.image_src = ROCK_IMAGE
            case RPSMove.PAPER:
                self.image_container.image_src = PAPER_IMAGE
            case RPSMove.SCISSORS:
                self.image_container.image_src = SCISSORS_IMAGE
        self.image_container.update()


class GameContainer(ft.Container):
    """
    Game window container component.
    Stores all the game controls and relevant methods.
    """
    THEME_STYLE: ft.TextThemeStyle = ft.TextThemeStyle.HEADLINE_LARGE
    FONT: str = "Consolas"

    def __init__(self, game: RPSGame) -> None:
        self.game: RPSGame = game

        self.turn_counter = ft.Text(theme_style=self.THEME_STYLE, font_family=self.FONT)
        self.round_result = ft.Text(theme_style=self.THEME_STYLE, font_family=self.FONT)
        self.player_score = ft.Text(theme_style=self.THEME_STYLE, font_family=self.FONT)
        self.bot_score = ft.Text(theme_style=self.THEME_STYLE, font_family=self.FONT)

        self.player_screen = PlayerScreen(PLAYER_IMAGE)
        self.bot_screen = PlayerScreen(BOT_IMAGE)

        super().__init__(
            width=800,
            height=700,
            margin=10,
            bgcolor="#4B0082",
            image_src="assets/background.jpg",
            image_fit=ft.ImageFit.FILL,
            border_radius=40,
            border=ft.border.all(0.5, "white"),
            alignment=ft.alignment.center,
        )

    def on_move(self, move: RPSMove) -> None:
        """
        Move button handler. Processes the move and updates the game state.
        :param move: Player's move to process
        :return: None
        """
        game_state = self.game.move(move)
        self.update_content(game_state)

    def restart_game(self) -> None:
        """
        Restarts the game and updates the user view.
        :return: None
        """
        self.game.restart_game()
        self.page.close_dialog()
        self.update_content(self.game.state)
        self.page.update()

    def finish_game(self, game_status: GameStatus) -> None:
        """
        Invokes alert box when game is finished.
        :param game_status: The result of the game.
        :return: None
        """
        message_control = ft.Text(theme_style=self.THEME_STYLE, font_family=self.FONT)
        match game_status:
            case GameStatus.WIN:
                message_control.value = "You won!"
                message_control.color = "green"
            case GameStatus.LOSS:
                message_control.value = "You lost!"
                message_control.color = "red"
            case GameStatus.DRAW:
                message_control.value = "It's a draw!"
                message_control.color = "white"

        restart_button = ft.FilledButton("Restart",
                                         icon=ft.icons.RESTART_ALT,
                                         on_click=lambda _: self.restart_game())
        exit_button = ft.FilledButton("Exit",
                                      icon=ft.icons.EXIT_TO_APP,
                                      on_click=lambda _: close_app(self.page))

        dialog = ft.AlertDialog(
            title=message_control,
            content=ft.Row(
                [restart_button, exit_button],
                alignment=ft.alignment.center
            ),
            on_dismiss=lambda _: self.restart_game()
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def set_round_result(self, round_result: RoundResult) -> None:
        """
        Sets the content of the round result text component.
        :param round_result: The result of the round
        :return: None
        """
        match round_result:
            case RoundResult.WIN:
                self.round_result.value = "WIN"
                self.round_result.color = "green"
            case RoundResult.LOSS:
                self.round_result.value = "LOSS"
                self.round_result.color = "red"
            case RoundResult.TIE:
                self.round_result.value = "TIE"
                self.round_result.color = "grey"
            case RoundResult.NONE:
                self.round_result.value = ""

    def update_content(self, game_state: GameState) -> None:
        """
        Updates the contents of the game components based on the current game state.
        :param game_state: current state of the game.
        :return: None
        """
        self.turn_counter.value = f"Turn: {game_state.turn}"
        self.bot_score.value = f"Bot: {game_state.bot_score}"
        self.player_score.value = f"Player: {game_state.player_score}"
        if not game_state.history:
            self.player_screen.set_move_image()
            self.bot_screen.set_move_image()
            self.set_round_result(RoundResult.NONE)
            return
        player_move, bot_move, round_result = game_state.get_last_round()
        self.player_screen.set_move_image(player_move)
        self.bot_screen.set_move_image(bot_move)
        self.set_round_result(round_result)

        if game_state.is_finished():
            self.finish_game(game_state.status)

        self.update()

    def generate_content(self) -> None:
        """
        Renders all the game components.
        :return: None
        """
        self.update_content(self.game.state)

        rock_btn = MoveButton(lambda _: self.on_move(RPSMove.ROCK),
                                   image_url=ROCK_IMAGE,
                                   bg_color="red")
        paper_btn = MoveButton(lambda _: self.on_move(RPSMove.PAPER),
                                    image_url=PAPER_IMAGE,
                                    bg_color="green")
        scissors_btn = MoveButton(lambda _: self.on_move(RPSMove.SCISSORS),
                                       image_url=SCISSORS_IMAGE,
                                       bg_color="blue")

        content = ft.Column(
            [
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.turn_counter, self.round_result]
                ),
                ft.Container(
                    ft.Row(
                        height=400,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[self.player_screen, self.bot_screen]
                    ),
                ),
                ft.Container(
                    ft.Row(
                        [rock_btn, paper_btn, scissors_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=10,
                ),
                ft.Divider(
                    thickness=1,
                    color="white"
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.player_score, self.bot_score]
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.content = content
        self.update()


def close_app(page: ft.Page) -> None:
    """
    Closes the application.
    :param page: page to close.
    :return: None
    """
    page.window_destroy()


def main(page: ft.Page) -> None:
    """
    Flet app target function.
    :param page: flet page.
    :return: None
    """
    page.title = "Rock Paper Scissors"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    game = RPSGame()
    game_container = GameContainer(game)
    page.add(game_container)
    game_container.generate_content()
    page.add(
        ft.Row(
            [
                ft.FilledButton("Restart",
                                icon=ft.icons.RESTART_ALT,
                                on_click=lambda _: game_container.restart_game()
                                ),
                ft.FilledButton("Exit",
                                icon=ft.icons.EXIT_TO_APP,
                                on_click=lambda _: close_app(page)
                                )
            ],
            alignment=ft.MainAxisAlignment.CENTER

        )
    )


if __name__ == '__main__':
    ft.app(target=main)
