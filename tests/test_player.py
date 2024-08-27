import unittest
import pygame
from unittest.mock import patch, MagicMock
from src.game_logic.player import Player, Human, Bot
from model.model_manager import ModelManager


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


class MockSurface:
    def get_rect(self, **kwargs):
        return pygame.Rect(0, 0, 100, 50)

    def inflate(self, x, y):
        return pygame.Rect(0, 0, 100 + x, 50 + y)


@patch("pygame.image.load", return_value=MockSurface())
@patch("pygame.transform.scale", return_value=MockSurface())
@patch("pygame.display.flip")
@patch("pygame.font.Font", return_value=MagicMock())
class TestHumanPlayer(unittest.TestCase):

    def setUp(self):
        self.screen = MockScreen()
        self.human = Human("Player1", self.screen)
        self.human.hand = ["card_path1", "card_path2", "card_path3"]

    def test_storyteller_turn(self, mock_font, mock_flip, mock_scale, mock_load):
        with patch.object(
            Human, "choose_card", return_value="card_path1"
        ), patch.object(Human, "input_clue", return_value="Clue"):
            card, clue = self.human.storyteller_turn()
            self.assertEqual(card, "card_path1")
            self.assertEqual(clue, "Clue")

    def test_choose_card(self, mock_font, mock_flip, mock_scale, mock_load):
        with patch.object(
            Human,
            "handle_events_card_selection",
            side_effect=lambda: setattr(self.human, "selected_card_index", 0),
        ):
            chosen_card = self.human.choose_card()
            self.assertEqual(chosen_card, "card_path1")
            self.assertEqual(len(self.human.hand), 2)

    def test_input_clue(self, mock_font, mock_flip, mock_scale, mock_load):
        # Create a mock event for pressing the RETURN key
        mock_event_return = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        # Mock pygame.event.get to return this mock event
        with patch("pygame.event.get", return_value=[mock_event_return]):
            clue = self.human.input_clue()
            self.assertEqual(clue, "")

    def test_vote(self, mock_font, mock_flip, mock_scale, mock_load):
        table = [(1, "card1"), (2, "card2"), (3, "card3")]
        with patch.object(
            Human,
            "handle_events_vote_selection",
            side_effect=lambda table: setattr(self.human, "selected_vote_index", 1),
        ):
            vote = self.human.vote(table, "Clue")
            self.assertEqual(vote, 1)


    def test_render_hand(self, mock_font, mock_flip, mock_scale, mock_load):
        self.human.render_hand()
        self.assertTrue(mock_load.called)
        self.assertTrue(mock_scale.called)


@patch("pygame.display.flip")
class TestBotPlayer(unittest.TestCase):

    def setUp(self):
        self.model_manager = MagicMock(spec=ModelManager)
        self.bot = Bot(self.model_manager)
        self.bot.hand = ["card_path1", "card_path2", "card_path3"]

    def test_storyteller_turn(self, mock_flip):
        card, clue = self.bot.storyteller_turn()
        self.assertIn(card, self.bot.hand)
        self.assertTrue(clue.startswith("Generated Clue for"))

    def test_choose_card_based_on_clue(self, mock_flip):
        chosen_card = self.bot.choose_card_based_on_clue("Clue")
        self.assertIn(chosen_card, self.bot.hand)

    def test_vote(self, mock_flip):
        table = [(1, "card1"), (2, "card2"), (3, "card3")]
        vote = self.bot.vote(table, "Clue")
        self.assertIn(vote, range(len(table)))


if __name__ == "__main__":
    unittest.main()
