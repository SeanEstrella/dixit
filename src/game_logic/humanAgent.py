import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN


class Human:
    _id_counter = 0

    def __init__(self, name, screen):
        self.id = Human._id_counter
        Human._id_counter += 1
        self.name = name
        self.hand = []
        self.score = 0
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.selected_card_index = None
        self.selected_vote_index = None

    def choose_card(self):
        while self.selected_card_index is None:
            self.screen.fill((0, 0, 128))
            self.render_hand()
            pygame.display.flip()
            self.handle_events_card_selection()

        chosen_card = self.hand.pop(self.selected_card_index)
        self.selected_card_index = None
        return chosen_card

    def render_hand(self):
        x_offset = 50
        y_position = self.screen.get_height() * 0.75

        for i, card_path in enumerate(self.hand):
            card_image = pygame.image.load(card_path)
            card_image = pygame.transform.scale(
                card_image,
                (
                    int(self.screen.get_width() * 0.1),
                    int(self.screen.get_height() * 0.2),
                ),
            )
            card_rect = card_image.get_rect(topleft=(x_offset, y_position))
            self.screen.blit(card_image, card_rect)

            if self.selected_card_index == i:
                pygame.draw.rect(
                    self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2
                )

            x_offset += card_rect.width + 20

    def handle_events_card_selection(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_card_click(event.pos)

    def handle_card_click(self, mouse_pos):
        x_offset = 50
        y_position = self.screen.get_height() * 0.75

        for i, card_path in enumerate(self.hand):
            card_image = pygame.image.load(card_path)
            card_image = pygame.transform.scale(
                card_image,
                (
                    int(self.screen.get_width() * 0.1),
                    int(self.screen.get_height() * 0.2),
                ),
            )
            card_rect = card_image.get_rect(topleft=(x_offset, y_position))

            if card_rect.collidepoint(mouse_pos):
                self.selected_card_index = i
                break

            x_offset += card_rect.width + 20

    def vote(self, table):
        while self.selected_vote_index is None:
            self.screen.fill((0, 0, 128))
            self.render_table(table)
            pygame.display.flip()
            self.handle_events_vote_selection(table)

        chosen_vote = self.selected_vote_index
        self.selected_vote_index = None
        return chosen_vote

    def render_table(self, table):
        y_offset = 200
        vote_text = self.font.render(
            f"{self.name}, vote for the card you think is the storyteller's card:",
            True,
            (255, 255, 255),
        )
        self.screen.blit(vote_text, (100, 100))
        for i, (player_id, card) in enumerate(table):
            card_text = self.font.render(f"Card {i + 1}: {card}", True, (255, 255, 255))
            card_rect = self.screen.blit(card_text, (100, y_offset))
            if self.selected_vote_index == i:
                pygame.draw.rect(
                    self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2
                )
            y_offset += 50

    def handle_events_vote_selection(self, table):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                self.handle_vote_click(event.pos, table)

    def handle_vote_click(self, mouse_pos, table):
        y_offset = 200
        for i, (player_id, card) in enumerate(table):
            card_text = self.font.render(f"Card {i + 1}: {card}", True, (255, 255, 255))
            card_rect = self.screen.blit(card_text, (100, y_offset))
            if card_rect.collidepoint(mouse_pos):
                self.selected_vote_index = i
                break
            y_offset += 50

    def storyteller_turn(self):
        chosen_card = self.choose_card()
        clue = self.input_clue(chosen_card)
        return chosen_card, clue

    def input_clue(self, card):
        clue = ""
        input_active = True
        while input_active:
            self.screen.fill((0, 0, 128))
            input_text = self.font.render(
                f"Enter a clue for your card:", True, (255, 255, 255)
            )
            self.screen.blit(input_text, (100, 100))
            clue_text = self.font.render(clue, True, (255, 255, 255))
            self.screen.blit(clue_text, (100, 150))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        clue = clue[:-1]
                    else:
                        clue += event.unicode

        return clue
