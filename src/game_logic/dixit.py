import os
import random
from game_logic.humanAgent import Human
from game_logic.bot import Bot
from model_manager import ModelManager
import pygame

model_manager = ModelManager()


def setup_game(player_names, num_bots, screen):
    """Initialize the game by setting up human players and bots."""
    players = []
    for name in player_names:
        players.append(Human(name, screen))
    for _ in range(num_bots):
        players.append(Bot(model_manager))
    return players


def deal_cards(players, cur_deck, num_cards):
    """Deal a specified number of cards to each player."""
    if not cur_deck:
        raise ValueError("Deck is empty or not initialized.")

    random.shuffle(cur_deck)
    for player in players:
        if len(cur_deck) < num_cards:
            raise ValueError("Not enough cards in the deck.")
        player.hand.extend(cur_deck.pop() for _ in range(num_cards))
    return cur_deck


def storyteller_turn(storyteller, screen):
    """Handle the storyteller's turn to pick a card and provide a clue."""
    return storyteller.storyteller_turn(screen)


def collect_votes(players, storyteller, table, clue, screen):
    """Collect votes from all players except the storyteller."""
    votes = []
    for player in players:
        if player != storyteller:
            vote = player.vote(table, clue, screen)
            votes.append(vote)
    return votes


def collect_cards(players, storyteller_card, storyteller, clue, screen):
    """Collect cards from all players based on the clue given by the storyteller."""
    table = [(storyteller.id, storyteller_card)]
    for player in players:
        if player != storyteller:
            chosen_card = player.choose_card_based_on_clue(clue, screen)
            table.append((player.id, chosen_card))
    random.shuffle(table)
    return table


def score_round(players, storyteller, storyteller_card, table, votes):
    """Score the current round based on the votes and cards played."""
    storyteller_card_index = next(
        (i for i, (_, card) in enumerate(table) if card == storyteller_card), None
    )
    if storyteller_card_index is None:
        raise ValueError("Storyteller's card not found on the table.")

    correct_votes = votes.count(storyteller_card_index)
    if correct_votes == 0 or correct_votes == len(players) - 1:
        for player in players:
            if player != storyteller:
                player.score += 2
    else:
        storyteller.score += 3
        for player, vote in zip(players, votes):
            if vote == storyteller_card_index:
                player.score += 3

    for player in players:
        if player != storyteller:
            player_votes = sum(1 for vote in votes if table[vote][0] == player.id)
            player.score += player_votes


def play_game(players, cur_deck, num_cards, screen, game_manager):
    """Main game loop to play the game with all rounds and score updates."""
    if not game_manager:
        raise ValueError("Game manager is not initialized.")

    while cur_deck:
        storyteller = game_manager.get_storyteller()
        storyteller_card, clue = storyteller_turn(storyteller, screen)
        table = collect_cards(players, storyteller_card, storyteller, clue, screen)
        votes = collect_votes(players, storyteller, table, clue, screen)
        score_round(players, storyteller, storyteller_card, table, votes)
        display_scores(players, screen)

        if not continue_game(screen):
            display_final_scores(players, screen)
            break

        cur_deck = deal_cards(players, cur_deck, num_cards)
        game_manager.next_storyteller()


def load_images_from_directory(directory):
    """Load all image files from a directory into a list."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")

    return [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.lower().endswith((".png", ".jpg", ".jpeg"))
    ]


def display_scores(players, screen):
    """Display the current scores of all players."""
    screen.fill((0, 0, 128))
    font = pygame.font.Font(None, 50)
    y_offset = 100
    for player in players:
        score_text = font.render(
            f"{player.name}: {player.score} points", True, (255, 255, 255)
        )
        screen.blit(score_text, (100, y_offset))
        y_offset += 50
    pygame.display.flip()
    pygame.time.wait(3000)


def continue_game(screen):
    """Ask the player if they want to continue the game."""
    screen.fill((0, 0, 128))
    font = pygame.font.Font(None, 50)
    question_text = font.render(
        "Do you want to play another round? (Yes/No)", True, (255, 255, 255)
    )
    screen.blit(question_text, (100, 100))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False


def display_final_scores(players, screen):
    """Display the final scores and announce the winner."""
    screen.fill((0, 0, 128))
    font = pygame.font.Font(None, 50)
    y_offset = 100
    for player in players:
        score_text = font.render(
            f"Final Score - {player.name}: {player.score} points", True, (255, 255, 255)
        )
        screen.blit(score_text, (100, y_offset))
        y_offset += 50

    max_score = max(player.score for player in players)
    winners = [player.name for player in players if player.score == max_score]

    winner_text = font.render(
        (
            f"The winner is {', '.join(winners)}!"
            if len(winners) == 1
            else f"It's a tie between: {', '.join(winners)}!"
        ),
        True,
        (255, 255, 255),
    )
    screen.blit(winner_text, (100, y_offset))
    pygame.display.flip()
    pygame.time.wait(5000)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dixit")

    players = setup_game(["Player1", "Player2"], 1, screen)
    deck = load_images_from_directory("data/cards")
    cur_deck = deal_cards(players, deck, 6)

    play_game(players, cur_deck, 6, screen, None)
