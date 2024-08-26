import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, K_RETURN

MAX_PLAYERS = 4  # Maximum number of human players
MAX_BOTS = 4  # Maximum number of bot players


class SetupMenu:
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (0, 0, 128)  # Blue background color
        screen_width, screen_height = screen.get_size()
        base_font_size = int(screen_height * 0.05)  # Font size based on screen height
        self.font = pygame.font.Font(None, base_font_size)

        self.buttons = {
            "increase_humans": {
                "text": "Increase Human Players",
                "pos": None,
                "rect": None,
            },
            "decrease_humans": {
                "text": "Decrease Human Players",
                "pos": None,
                "rect": None,
            },
            "increase_bots": {
                "text": "Increase Bot Players",
                "pos": None,
                "rect": None,
            },
            "decrease_bots": {
                "text": "Decrease Bot Players",
                "pos": None,
                "rect": None,
            },
            "proceed": {"text": "Proceed", "pos": None, "rect": None},
        }

        self.num_humans = 0
        self.num_bots = 0

    def render(self):
        self.screen.fill(self.background_color)

        # Get the dimensions of the screen
        screen_width, screen_height = self.screen.get_size()

        # Define spacing and positions
        y_offset_top = int(screen_height * 0.1)  # Top spacing for humans and bots
        button_spacing = int(screen_height * 0.05)  # Vertical spacing between buttons

        # Render Humans and Bots count
        humans_text = self.font.render(
            f"Humans: {self.num_humans}", True, (255, 255, 255)
        )
        bots_text = self.font.render(f"Bots: {self.num_bots}", True, (255, 255, 255))
        self.screen.blit(humans_text, (int(screen_width * 0.1), y_offset_top))
        self.screen.blit(
            bots_text, (int(screen_width * 0.1), y_offset_top + button_spacing)
        )

        # Define the positions for the increase/decrease buttons
        self.buttons["increase_humans"]["pos"] = (
            int(screen_width * 0.1),
            y_offset_top + button_spacing * 2,
        )
        self.buttons["decrease_humans"]["pos"] = (
            screen_width
            - int(screen_width * 0.1)
            - self.font.size("Decrease Human Players")[0],
            y_offset_top + button_spacing * 2,
        )

        self.buttons["increase_bots"]["pos"] = (
            int(screen_width * 0.1),
            y_offset_top + button_spacing * 3,
        )
        self.buttons["decrease_bots"]["pos"] = (
            screen_width
            - int(screen_width * 0.1)
            - self.font.size("Decrease Bot Players")[0],
            y_offset_top + button_spacing * 3,
        )

        # Render the increase/decrease buttons and set their rects
        for key, button in self.buttons.items():
            if key != "proceed":  # "proceed" button is handled separately
                text_surface = self.font.render(button["text"], True, (255, 255, 255))
                button["rect"] = text_surface.get_rect(topleft=button["pos"])
                self.screen.blit(text_surface, button["pos"])

        # Position and render the "Proceed" button in the middle of the screen
        proceed_text = self.font.render("Proceed", True, (255, 255, 255))
        self.buttons["proceed"]["rect"] = proceed_text.get_rect(
            center=(screen_width // 2, screen_height - int(screen_height * 0.1))
        )
        self.screen.blit(proceed_text, self.buttons["proceed"]["rect"].topleft)

        pygame.display.flip()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                for key, button in self.buttons.items():
                    if button["rect"] and button["rect"].collidepoint(event.pos):
                        if key == "increase_humans":
                            self.num_humans = min(self.num_humans + 1, MAX_PLAYERS)
                        elif key == "decrease_humans":
                            self.num_humans = max(0, self.num_humans - 1)
                        elif key == "increase_bots":
                            self.num_bots = min(self.num_bots + 1, MAX_BOTS)
                        elif key == "decrease_bots":
                            self.num_bots = max(0, self.num_bots - 1)
                        elif key == "proceed":
                            return (
                                "player_name_input_screen",
                                self.num_humans,
                                self.num_bots,
                            )

        return None, self.num_humans, self.num_bots
