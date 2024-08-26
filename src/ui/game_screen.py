import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, K_RETURN
from game_logic.humanAgent import Human
import random
from game_logic.dixit import deal_cards


class GameScreen:
    def __init__(self, screen, players, cur_deck, game_manager):
        self.screen = screen
        self.players = players
        self.cur_deck = cur_deck
        self.game_manager = game_manager

        # Load background image safely
        try:
            self.background_image = pygame.image.load("data/background.jpg")
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            self.background_image = None

        self.font = pygame.font.Font(None, int(self.screen.get_height() * 0.05))
        self.score_font = pygame.font.Font(None, int(self.screen.get_height() * 0.04))

        self.current_player_index = 0
        self.selected_card_index = None
        self.entering_clue = False
        self.clue = ""
        self.storyteller_clue_submitted = False
        self.voting_phase = False
        self.round_ended = False

        self.card_positions = []
        self.selected_cards = []
        self.votes = []
        self.next_round_button = pygame.Rect(
            self.screen.get_width() * 0.75, self.screen.get_height() * 0.85, 200, 50
        )

    def render(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 0))  # Default to black background if image fails

        self.display_scores()
        self.display_storyteller_info()
        self.display_clue()
        self.render_player_hand()
        self.render_selected_cards()

        if self.round_ended:
            self.render_next_round_button()

        pygame.display.flip()

        if not self.round_ended:
            self.process_bot_turn()

    def render_next_round_button(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.next_round_button)
        text_surface = self.font.render("Next Round", True, (0, 0, 0))
        self.screen.blit(
            text_surface,
            (
                self.next_round_button.centerx - text_surface.get_width() // 2,
                self.next_round_button.centery - text_surface.get_height() // 2,
            ),
        )

    def display_scores(self):
        x_offset = self.screen.get_width() * 0.75
        y_position = self.screen.get_height() * 0.05
        for player in self.players:
            score_text = f"{player.name}: {player.score} points"
            score_surface = self.score_font.render(score_text, True, (255, 255, 255))
            self.screen.blit(score_surface, (x_offset, y_position))
            y_position += score_surface.get_height() + 5

    def display_storyteller_info(self):
        storyteller = self.game_manager.get_storyteller()
        storyteller_text = self.font.render(
            f"Storyteller: {storyteller.name}", True, (255, 255, 255)
        )
        self.screen.blit(
            storyteller_text,
            (self.screen.get_width() * 0.05, self.screen.get_height() * 0.05),
        )

    def display_clue(self):
        if self.storyteller_clue_submitted or self.entering_clue:
            clue_display = (
                f"Clue: {self.clue}"
                if self.storyteller_clue_submitted
                else f"Enter Clue: {self.clue}"
            )
            clue_text = self.font.render(clue_display, True, (255, 255, 255))
            self.screen.blit(
                clue_text,
                (self.screen.get_width() * 0.05, self.screen.get_height() * 0.15),
            )

    def render_player_hand(self):
        player = self.players[self.current_player_index]
        if isinstance(player, Human):
            self.render_hand(player)

    def render_hand(self, player):
        x_offset = self.screen.get_width() * 0.05
        y_position = self.screen.get_height() * 0.75
        self.card_positions = []

        card_width = self.screen.get_width() * 0.1
        card_height = self.screen.get_height() * 0.2

        for i, card_path in enumerate(player.hand):
            card_image = self.load_card_image(card_path, card_width, card_height)
            card_rect = card_image.get_rect(topleft=(x_offset, y_position))
            self.screen.blit(card_image, card_rect)
            self.card_positions.append(card_rect)

            if self.selected_card_index == i:
                self.highlight_selected_card(card_rect)

            x_offset += card_rect.width + 20

    def load_card_image(self, card_path, width, height):
        try:
            card_image = pygame.image.load(card_path)
            return pygame.transform.scale(card_image, (int(width), int(height)))
        except pygame.error as e:
            print(f"Error loading card image: {e}")
            return pygame.Surface((int(width), int(height)))  # Return a blank surface

    def highlight_selected_card(self, card_rect):
        pygame.draw.rect(self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2)

    def render_selected_cards(self):
        x_offset = self.screen.get_width() * 0.05
        y_position = self.screen.get_height() * 0.3

        card_width = self.screen.get_width() * 0.1
        card_height = self.screen.get_height() * 0.2

        for card_path in self.selected_cards:
            card_image = self.load_card_image(card_path, card_width, card_height)
            card_rect = card_image.get_rect(topleft=(x_offset, y_position))
            self.screen.blit(card_image, card_rect)
            x_offset += card_rect.width + 20

    def process_bot_turn(self):
        player = self.players[self.current_player_index]
        if not isinstance(player, Human):
            pygame.time.wait(1000)
            self.selected_card_index = random.choice(range(len(player.hand)))
            self.handle_card_selection()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and not self.entering_clue:
                if self.round_ended and self.next_round_button.collidepoint(event.pos):
                    self.start_new_round()
                elif self.voting_phase:
                    self.handle_vote_click(event.pos)
                else:
                    self.handle_card_click(event.pos)
            elif event.type == KEYDOWN and self.entering_clue:
                self.handle_clue_typing(event)

        if not self.cur_deck:
            return "game_over"

    def handle_clue_typing(self, event):
        if event.key == K_RETURN:
            self.handle_clue_submission()
        elif event.key == K_BACKSPACE:
            self.clue = self.clue[:-1]
        else:
            self.clue += event.unicode

    def handle_card_click(self, mouse_pos):
        for i, rect in enumerate(self.card_positions):
            if rect.collidepoint(mouse_pos):
                self.selected_card_index = i
                self.handle_card_selection()
                break

    def handle_vote_click(self, mouse_pos):
        for i, rect in enumerate(self.card_positions):
            if rect.collidepoint(mouse_pos):
                self.votes.append(i)
                self.advance_to_next_player()
                if self.is_voting_complete():
                    self.calculate_scores()
                break

    def handle_card_selection(self):
        player = self.players[self.current_player_index]
        selected_card = player.hand.pop(self.selected_card_index)
        self.selected_cards.append(selected_card)

        if self.is_storyteller(player):
            self.prompt_clue(selected_card)
        else:
            self.advance_to_next_player()

        if self.is_round_complete():
            self.round_ended = True

    def is_storyteller(self, player):
        return player == self.game_manager.get_storyteller()

    def prompt_clue(self, card):
        self.entering_clue = True
        self.clue = ""

    def handle_clue_submission(self):
        self.storyteller_clue_submitted = True
        self.advance_to_next_player()
        self.entering_clue = False
        self.selected_card_index = None
        self.voting_phase = True

    def advance_to_next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def is_round_complete(self):
        return self.current_player_index == 0 and self.storyteller_clue_submitted

    def is_voting_complete(self):
        return len(self.votes) == len(self.players) - 1

    def calculate_scores(self):
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

        self.voting_phase = False
        self.round_ended = True

    def start_new_round(self):
        if len(self.cur_deck) < 6 * len(self.players):
            print("Not enough cards left in the deck for a new round.")
            return

        self.game_manager.next_storyteller()
        self.current_player_index = 0
        self.clue = ""
        self.selected_card_index = None
        self.storyteller_clue_submitted = False
        self.cur_deck = deal_cards(self.players, self.cur_deck, 6)
        self.selected_cards = []
        self.votes = []
        self.round_ended = False
        self.render()
