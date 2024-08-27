import pygame

def render_background(screen, background_image_path):
    try:
        background = pygame.image.load(background_image_path)
        screen.blit(background, (0, 0))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        screen.fill((0, 0, 0))

def render_hand(screen, hand, selected_card_index=None):
    x_offset = 50
    y_position = screen.get_height() * 0.75
    card_positions = []
    for i, card_path in enumerate(hand):
        card_rect = render_card(screen, card_path, (x_offset, y_position))
        card_positions.append(card_rect)
        if selected_card_index == i:
            pygame.draw.rect(screen, (255, 255, 0), card_rect.inflate(10, 10), 2)
        x_offset += card_rect.width + 20
    return card_positions

def render_card(screen, card_path, position):
    try:
        card_image = pygame.image.load(card_path)
        card_image = pygame.transform.scale(
            card_image, (int(screen.get_width() * 0.1), int(screen.get_height() * 0.2))
        )
        card_rect = card_image.get_rect(topleft=position)
        screen.blit(card_image, card_rect)
        return card_rect
    except pygame.error as e:
        print(f"Error loading card image {card_path}: {e}")
        return pygame.Rect(position[0], position[1], 0, 0)

def render_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)
    return text_surface
