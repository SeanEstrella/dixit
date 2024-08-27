import pygame
import sys
import random
import logging
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, K_RETURN, VIDEORESIZE
from core.state_machine import (
    GameState,
    WaitingForPlayerInput,
    ClueSubmissionState,
    VotingState,
    RoundEndState,
)
from utils.rendering import render_background, render_hand, render_card
from game_logic.player import Human
from typing import List, Optional

class GameScreen:
    def __init__(self, screen: pygame.Surface, players: List[Human], cur_deck: List[str], game_manager):
        self.screen = screen
        self.players = players
        self.cur_deck = cur_deck
        self.game_manager = game_manager
        self.current_clue_input = ""

        # Set up fonts and background
        self._setup_fonts()
        self.background_image = "data/background.jpg"  # Path to the background image
        self.image_cache = {}  # Cache for card images

        # Game state variables
        self.current_player_index = 0
        self.selected_card_index: Optional[int] = None
        self.clue = ""
        self.storyteller_clue_submitted = False
        self.card_positions = []
        self.selected_cards = []
        self.votes = []
        self.next_round_button = pygame.Rect(
            self.screen.get_width() * 0.75, self.screen.get_height() * 0.85, 200, 50
        )

        # Initialize state
        self.state = WaitingForPlayerInput(self)
        logging.debug("GameScreen initialized.")

    def _setup_fonts(self):
        """Initialize fonts for rendering text."""
        try:
            self.font = pygame.font.Font(None, int(self.screen.get_height() * 0.05))
            self.score_font = pygame.font.Font(None, int(self.screen.get_height() * 0.04))
        except pygame.error as e:
            logging.error(f"Error loading font: {e}", exc_info=True)
            pygame.quit()
            sys.exit(1)

    def handle_event(self, events):
        """Handle all incoming events."""
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (MOUSEBUTTONDOWN, KEYDOWN):
                try:
                    self.state.handle_input(event)
                except Exception as e:
                    logging.error(f"Error handling event {event.type}: {e}", exc_info=True)
            elif event.type == VIDEORESIZE:
                self._handle_resize(event.size)

    def _handle_resize(self, size):
        """Handle window resize events."""
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.render_background()
        self.render()

    def update(self):
        """Update the current state."""
        self.state.update()

    def render(self):
        """Main render method to display all necessary game elements."""
        self.render_background()
        self.render_player_hand()
        self.render_scores()
        self.render_storyteller_info()
        self.render_clue()
        self.render_selected_cards()
        pygame.display.flip()
        logging.debug("GameScreen rendered.")

    def render_background(self):
        render_background(self.screen, self.background_image)

    def render_player_hand(self):
        """Render the current player's hand of cards."""
        player = self.players[self.current_player_index]
        self.card_positions = render_hand(
            self.screen, player.hand, self.selected_card_index
        )

    def render_selected_cards(self):
        """Render the selected cards on the table."""
        x_offset = self.screen.get_width() * 0.05
        y_position = self.screen.get_height() * 0.3
        card_width = self.screen.get_width() * 0.1
        card_height = self.screen.get_height() * 0.2

        for card_path in self.selected_cards:
            card_image = self.load_card_image(card_path, card_width, card_height)
            card_rect = card_image.get_rect(topleft=(x_offset, y_position))
            self.screen.blit(card_image, card_rect)
            x_offset += card_rect.width + 20

    def render_scores(self):
        """Render the current scores for all players."""
        y_offset = 20
        for player in self.players:
            score_text = f"{player.name}: {player.score} points"
            score_surface = self.font.render(score_text, True, (255, 255, 255))
            self.screen.blit(score_surface, (20, y_offset))
            y_offset += score_surface.get_height() + 10

    def render_storyteller_info(self):
        """Render information about the current storyteller."""
        storyteller = self.game_manager.get_storyteller()
        storyteller_text = f"Storyteller: {storyteller.name}"
        storyteller_surface = self.font.render(storyteller_text, True, (255, 215, 0))
        self.screen.blit(storyteller_surface, (self.screen.get_width() - 250, 20))

    def render_clue(self):
        """Render the current clue provided by the storyteller."""
        if self.clue:
            clue_text = f"Clue: {self.clue}"
            clue_surface = self.font.render(clue_text, True, (255, 255, 255))
            self.screen.blit(clue_surface, (self.screen.get_width() // 2 - clue_surface.get_width() // 2, 20))

    def handle_clue_typing(self, event):
        """Handle typing events to input the clue."""
        if event.key == K_RETURN:
            self.handle_clue_submission()
        elif event.key == K_BACKSPACE:
            self.current_clue_input = self.current_clue_input[:-1]
        else:
            self.current_clue_input += event.unicode

    def handle_card_selection(self):
        """Handle the logic when a card is selected."""
        player = self.players[self.current_player_index]

        if self.selected_card_index is None or not (
            0 <= self.selected_card_index < len(player.hand)
        ):
            logging.error("Error: selected_card_index is out of range or invalid.")
            return

        selected_card = player.hand.pop(self.selected_card_index)
        self.selected_cards.append(selected_card)

        if self.is_storyteller(player):
            self.state = ClueSubmissionState(self)
        else:
            self.advance_to_next_player()

        if self.is_round_complete():
            self.state = RoundEndState(self)
            logging.info("Round complete. Waiting for next round to start.")

    def handle_clue_submission(self):
        self.clue = self.current_clue_input  # Set the clue
        self.storyteller_clue_submitted = True
        self.advance_to_next_player()
        self.selected_card_index = None
        self.state = VotingState(self)

    def advance_to_next_player(self):
        """Advance to the next player's turn."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.process_bot_turn()

    def is_storyteller(self, player):
        """Check if the current player is the storyteller."""
        return player == self.game_manager.get_storyteller()

    def is_round_complete(self):
        """Check if the round is complete."""
        return self.current_player_index == 0 and self.storyteller_clue_submitted

    def calculate_scores(self):
        """Calculate the scores after voting."""
        storyteller = self.game_manager.get_storyteller()
        storyteller_card_index = self.selected_cards.index(storyteller.hand[0])

        correct_votes = sum(1 for vote in self.votes if vote == storyteller_card_index)
        if correct_votes == 0 or correct_votes == len(self.players) - 1:
            for player in self.players:
                if player != storyteller:
                    player.score += 2
        else:
            storyteller.score += 3
            for player, vote in zip(self.players, self.votes):
                if vote == storyteller_card_index:
                    player.score += 3
                else:
                    player.score += 1

        self.state = RoundEndState(self)

    def render_next_round_button(self):
        """Render the button to start the next round."""
        pygame.draw.rect(self.screen, (255, 255, 255), self.next_round_button)
        text_surface = self.font.render("Next Round", True, (0, 0, 0))
        self.screen.blit(
            text_surface,
            (
                self.next_round_button.centerx - text_surface.get_width() // 2,
                self.next_round_button.centery - text_surface.get_height() // 2,
            ),
        )

    def handle_card_click(self, mouse_pos):
        """Handle mouse click events to select a card."""
        for i, rect in enumerate(self.card_positions):
            if rect.collidepoint(mouse_pos):
                self.selected_card_index = i
                self.handle_card_selection()
                break

    def handle_vote_click(self, mouse_pos):
        """Handle mouse click events to vote on a card."""
        for i, rect in enumerate(self.card_positions):
            if rect.collidepoint(mouse_pos):
                self.votes.append(i)
                self.advance_to_next_player()
                if self.is_voting_complete():
                    self.calculate_scores()
                break

    def is_voting_complete(self):
        """Check if the voting phase is complete."""
        return len(self.votes) == len(self.players) - 1

    def process_bot_turn(self):
        """Process the bot player's turn."""
        player = self.players[self.current_player_index]
        if not isinstance(player, Human):
            if player.hand:
                self.selected_card_index = random.choice(range(len(player.hand)))
                self.handle_card_selection()
            self.game_manager.just_dealt = False

    def start_new_round(self):
        """Start a new round."""
        logging.info("Starting a new round.")
        self.current_player_index = 0  # Reset player index if needed
        self.round_ended = False
        self.storyteller_clue_submitted = False
        self.votes = []
        self.selected_cards = []
        self.state = WaitingForPlayerInput(self)

    def load_card_image(self, card_path, width, height):
        """Utility function to load, scale, and render a card image."""
        cache_key = (card_path, width, height)
        if cache_key not in self.image_cache:
            try:
                card_image = pygame.image.load(card_path)
                card_image = pygame.transform.scale(card_image, (int(width), int(height)))
                self.image_cache[cache_key] = card_image
            except pygame.error as e:
                logging.error(f"Error loading card image {card_path}: {e}", exc_info=True)
                return pygame.Surface((int(width), int(height)))
        return self.image_cache[cache_key]
