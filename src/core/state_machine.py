from abc import ABC, abstractmethod
import pygame
import sys


class GameState(ABC):
    def __init__(self, game_screen):
        self.game_screen = game_screen

    @abstractmethod
    def handle_input(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass


class WaitingForPlayerInput(GameState):
    def handle_input(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.game_screen.handle_card_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.game_screen.handle_clue_typing(event)

    def update(self):
        if self.game_screen.selected_card_index is not None:
            if self.game_screen.is_storyteller_turn():
                self.game_screen.state = ClueSubmissionState(self.game_screen)
            else:
                self.game_screen.advance_to_next_player()
                if self.game_screen.is_round_complete():
                    self.game_screen.state = VotingState(self.game_screen)

    def render(self):
        self.game_screen.render_background()
        self.game_screen.render_player_hand()
        pygame.display.flip()


class ClueSubmissionState(GameState):
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.game_screen.handle_clue_typing(event)

    def update(self):
        if self.game_screen.storyteller_clue_submitted:
            self.game_screen.state = VotingState(self.game_screen)

    def render(self):
        self.game_screen.render_background()
        self.game_screen.display_clue_input()
        pygame.display.flip()


class VotingState(GameState):
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game_screen.handle_vote_click(event.pos)

    def update(self):
        if self.game_screen.is_voting_complete():
            self.game_screen.calculate_scores()
            self.game_screen.state = RoundEndState(self.game_screen)

    def render(self):
        self.game_screen.render_background()
        self.game_screen.render_selected_cards()
        pygame.display.flip()


class RoundEndState(GameState):
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.game_screen.next_round_button.collidepoint(event.pos):
                self.game_screen.start_new_round()
                self.game_screen.state = WaitingForPlayerInput(self.game_screen)

    def update(self):
        pass

    def render(self):
        self.game_screen.render_background()
        self.game_screen.render_scores()
        self.game_screen.render_next_round_button()
        pygame.display.flip()


class GameOverState(GameState):
    def handle_input(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def update(self):
        pass

    def render(self):
        self.game_screen.render_background()
        self.game_screen.display_game_over_message()
        pygame.display.flip()
