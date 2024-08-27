import unittest
import pygame
from core.game_manager import GameManager
from unittest.mock import patch, MagicMock


# Mock classes and methods
class MockScreen:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def fill(self, color):
        pass

    def blit(self, source, dest):
        pass

    def get_size(self):
        return self.width, self.height


class MockFont:
    def render(self, text, antialias, color):
        return MockSurface()


class MockSurface:
    def get_rect(self, **kwargs):
        return pygame.Rect(0, 0, 100, 50)

    def inflate(self, x, y):
        return pygame.Rect(0, 0, 100 + x, 50 + y)


class TestDixitGame(unittest.TestCase):

    @patch("pygame.display.set_mode")
    @patch("pygame.font.Font", return_value=MockFont())
    @patch("pygame.image.load", return_value=MockSurface())
    @patch("pygame.display.flip")
    @patch("pygame.draw.rect")
    @patch("pygame.display.set_caption")
    @patch("pygame.time.delay")
    @patch.object(GameManager, "handle_setup_menu", return_value=None)
    @patch.object(GameManager, "handle_player_name_input", return_value=None)
    def test_game_initialization(
        self,
        mock_player_name_input,
        mock_setup_menu,
        mock_delay,
        mock_caption,
        mock_rect,
        mock_flip,
        mock_image_load,
        mock_font,
        mock_set_mode,
    ):
        from core.game_manager import GameManager

        # Initialize mocked screen
        screen = MockScreen()

        # Initialize GameManager with mocked screen
        game_manager = GameManager(screen)

        # Manually set the player names and bots as they would be after user input
        game_manager.player_names = ["Player1", "Player2"]
        game_manager.num_bots = 1

        # Start the game and ensure it initializes correctly
        game_manager.start_game()

        # Debug output to check player initialization
        print(f"Number of players initialized: {len(game_manager.players)}")
        for player in game_manager.players:
            print(f"Player Name: {player.name}, Type: {type(player).__name__}")

        # Check if players and deck are initialized
        self.assertTrue(len(game_manager.players) > 0, "Players should be initialized.")
        self.assertTrue(len(game_manager.deck) > 0, "Deck should be loaded.")

    @patch("pygame.display.set_mode")
    @patch("pygame.font.Font", return_value=MockFont())
    @patch("pygame.image.load", return_value=MockSurface())
    @patch("pygame.display.flip")
    @patch("pygame.draw.rect")
    @patch("pygame.display.set_caption")
    @patch("pygame.time.delay")
    @patch.object(GameManager, "handle_setup_menu", return_value=None)
    @patch.object(GameManager, "handle_player_name_input", return_value=None)
    def test_first_round_execution(
        self,
        mock_player_name_input,
        mock_setup_menu,
        mock_delay,
        mock_caption,
        mock_rect,
        mock_flip,
        mock_image_load,
        mock_font,
        mock_set_mode,
    ):
        from core.game_manager import GameManager

        # Initialize mocked screen
        screen = MockScreen()

        # Initialize GameManager with mocked screen
        game_manager = GameManager(screen)

        # Manually set the player names and bots as they would be after user input
        game_manager.player_names = ["Player1", "Player2"]
        game_manager.num_bots = 1

        # Start the game (includes loading players and deck)
        game_manager.start_game()

        # Simulate the first storyteller's turn
        storyteller = game_manager.get_storyteller()
        card, clue = storyteller.storyteller_turn(screen)

        self.assertIsNotNone(card, "Storyteller should select a card.")
        self.assertIsInstance(clue, str, "Storyteller should provide a clue.")

        # Simulate the voting phase
        table = game_manager.collect_cards(
            game_manager.players, card, storyteller, clue, screen
        )
        votes = game_manager.collect_votes(
            game_manager.players, storyteller, table, clue, screen
        )

        self.assertEqual(
            len(votes),
            len(game_manager.players) - 1,
            "All players except storyteller should vote.",
        )

        # Check if the round is scored correctly
        game_manager.score_round()
        for player in game_manager.players:
            self.assertIsInstance(player.score, int, "Each player should have a score.")


if __name__ == "__main__":
    unittest.main()
