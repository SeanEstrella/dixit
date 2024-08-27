import pygame
import sys
import random
import logging
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, K_RETURN, VIDEORESIZE
from core.state_machine import (
    WaitingForPlayerInput,
    ClueSubmissionState,
    VotingState,
    RoundEndState,
)
from ui.base_screen import BaseScreen
from ui.rendering import Renderer
from game_logic.player import Human

logger = logging.getLogger('ui')

class GameScreen(BaseScreen):
    def __init__(self, screen, players, cur_deck, game_manager):
        super().__init__(screen)
        self.renderer = Renderer(screen)  # Use Renderer for all rendering tasks
        self.players = players
        self.cur_deck = cur_deck
        self.game_manager = game_manager
        self.current_clue_input = ""
        self.background_color = (0, 0, 128)
        self.font = self.load_font(int(screen.get_height() * 0.05))
        self.score_font = self.load_font(int(screen.get_height() * 0.04))

        # Game state variables
        self.current_player_index = 0
        self.selected_card_index = None
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
        logger.info("GameScreen initialized.")

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
                    logger.error(f"Error handling event {event.type}: {e}", exc_info=True)
            elif event.type == VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.render()
            else:
                pass

    def update(self):
        """Update the current state."""
        try:
            self.state.update()
        except Exception as e:
            logger.error(f"An error occurred during game execution: {str(e)}", exc_info=True)
            pygame.quit()
            sys.exit(1)

    def render(self):
        """Main render method to display all necessary game elements."""
        try:
            self.renderer.render_background(self.background_color)
            self.render_player_hand()
            self.render_scores()
            self.render_storyteller_info()
            self.render_clue()
            self.render_selected_cards()
            pygame.display.flip()
            logger.info("GameScreen rendered.")
        except Exception as e:
            logger.error(f"An error occurred during rendering: {str(e)}", exc_info=True)
            pygame.quit()
            sys.exit(1)

    def render_player_hand(self):
        """Render the current player's hand of cards."""
        player = self.players[self.current_player_index]
        self.card_positions = self.renderer.render_hand(player.hand, self.selected_card_index)

    def render_selected_cards(self):
        """Render the selected cards on the table."""
        self.renderer.render_selected_cards(self.selected_cards)

    def render_scores(self):
        """Render the current scores for all players."""
        y_offset = 20
        for player in self.players:
            score_text = f"{player.name}: {player.score} points"
            self.renderer.render_text(score_text, self.font, (255, 255, 255), (20, y_offset))
            y_offset += self.font.get_height() + 10

    def render_storyteller_info(self):
        """Render information about the current storyteller."""
        storyteller = self.game_manager.get_storyteller()
        storyteller_text = f"Storyteller: {storyteller.name}"
        self.renderer.render_text(storyteller_text, self.font, (255, 215, 0), (self.screen.get_width() - 250, 20))

    def render_clue(self):
        """Render the current clue provided by the storyteller."""
        if self.clue:
            clue_text = f"Clue: {self.clue}"
            self.renderer.render_text(clue_text, self.font, (255, 255, 255), (self.screen.get_width() // 2, 20), center=True)

    def render_next_round_button(self):
        """Render the button to start the next round."""
        pygame.draw.rect(self.screen, (255, 255, 255), self.next_round_button)
        self.renderer.render_text(
            "Next Round",
            self.font,
            (0, 0, 0),
            (self.next_round_button.centerx, self.next_round_button.centery),
            center=True
        )

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
            logger.error(f"Error: selected_card_index ({self.selected_card_index}) is out of range or invalid for hand size ({len(player.hand)}).")
            return

        selected_card = player.hand.pop(self.selected_card_index)
        self.selected_cards.append(selected_card)

        if self.is_storyteller(player):
            self.state = ClueSubmissionState(self)
        else:
            self.advance_to_next_player()

        if self.is_round_complete():
            self.state = RoundEndState(self)
            logger.info("Round complete. Waiting for next round to start.")

    def handle_clue_submission(self):
        """Handle the submission of a clue by the storyteller."""
        self.clue = self.current_clue_input
        self.storyteller_clue_submitted = True
        self.advance_to_next_player()
        self.selected_card_index = None
        self.state = VotingState(self)

    def advance_to_next_player(self):
        """Advance to the next player's turn."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if not isinstance(self.players[self.current_player_index], Human):
            self.process_bot_turn()

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
        logger.info("Starting a new round.")
        self.current_player_index = 0
        self.storyteller_clue_submitted = False
        self.votes = []
        self.selected_cards = []
        self.state = WaitingForPlayerInput(self)

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
