import logging
from players import Bot, Human
from scoring import score_clue_performance, adjust_generation_parameters
from deck import setup_deck, deal_cards
from model_manager import ModelManager

logger = logging.getLogger('game_logic')

MAX_ROUNDS = 10
SCORE_THRESHOLD = 30 
DEFAULT_BOT_COUNT = 3

def setup_players():
    """
    Setup the players for the game. Allows for both human and bot players.
    """
    model_manager = ModelManager()
    player_names = input("Enter player names, separated by commas (leave empty for bot-only game): ").split(',')
    player_names = [name.strip() for name in player_names if name.strip()]

    players = [Human(name=name, player_id=i) for i, name in enumerate(player_names)]

    if not players:
        logger.info("No human players detected. Starting a bot-only game.")
        players = [Bot(name=f"AI Bot {i+1}", player_id=i, model_manager=model_manager) for i in range(DEFAULT_BOT_COUNT)]
    else:
        bot_player = Bot(name="AI Bot", player_id=len(players), model_manager=model_manager)
        players.append(bot_player)

    logger.info(f"Players set up: {[player.name for player in players]}")
    return players

def initialize_game():
    """
    Initialize the game by setting up players and the deck.
    """
    try:
        players = setup_players()
        deck, discard_pile = setup_deck()
        deal_cards(players, deck, discard_pile, num_cards=6)
    except Exception as e:
        logger.error(f"Failed to initialize game: {e}")
        raise
    return players, deck, discard_pile

def rotate_storyteller(players, current_storyteller):
    """
    Rotate the storyteller to the next player.
    """
    current_index = players.index(current_storyteller)
    next_index = (current_index + 1) % len(players)
    logger.info(f"Rotating storyteller from {current_storyteller.name} to {players[next_index].name}.")
    return players[next_index]

def some_end_condition(round_number, players):
    """
    Determine if the game should end based on rounds or scores.
    """
    if round_number >= MAX_ROUNDS:
        logger.info(f"Maximum rounds ({MAX_ROUNDS}) reached.")
        return True
    for player in players:
        if player.score >= SCORE_THRESHOLD:
            logger.info(f"Player {player.name} reached the score threshold ({SCORE_THRESHOLD}).")
            return True
    return False

def terminal_game_loop():
    logger.info("Starting Dixit Bot Game...")

    players, deck, discard_pile = initialize_game()
    current_round = 1
    storyteller_index = 0
    
    while deck or any(player.hand for player in players):
        storyteller = players[storyteller_index]
        logger.info(f"\nNew Round {current_round}: {storyteller.name} is the storyteller.")

        if not storyteller.hand:
            logger.error(f"{storyteller.name} has no cards left. Ending game.")
            break

        card, clue = storyteller_turn(storyteller)
        if card is None:
            logger.error("Storyteller could not select a card. Ending game.")
            break

        table = player_choices(players, storyteller)
        if not table:
            logger.info("No cards available for choice. Ending game.")
            break

        votes = player_voting(players, storyteller, table, clue)
        logger.info(f"Votes cast: {votes}")

        score = calculate_score(votes, storyteller, table)
        logger.info(f"Score for this round: {score}")

        storyteller_index = (storyteller_index + 1) % len(players)
        current_round += 1

        if some_end_condition(current_round, players):
            logger.info("Game Ended by Condition Met.")
            break

    logger.info("Game Over! Thanks for playing!")
    
def storyteller_turn(storyteller):
    """
    Handle the storyteller's turn.
    """
    if not storyteller.hand:
        logger.error(f"{storyteller.name} has no cards left.")
        return None, None

    try:
        return storyteller.storyteller_turn()
    except Exception as e:
        logger.error(f"Error during storyteller turn: {e}")
        return None, None

def player_choices(players, storyteller):
    """
    Manage players' choices of cards.
    """
    table = [(storyteller.player_id, storyteller.selected_card)]
    for player in players:
        if player != storyteller and player.hand:
            chosen_card = player.choose_card()
            table.append((player.player_id, chosen_card))
    logger.info(f"Cards chosen by players: {table}")
    return table
    
def player_voting(players, storyteller, table, clue):
    """
    Manage voting phase where players guess the storyteller's card.
    """
    votes = []
    for player in players:
        if player != storyteller and player.hand:
            try:
                vote = player.vote(table, clue)
                votes.append(vote)
            except Exception as e:
                logger.warning(f"Error during voting by player {player.name}: {e}")
    return votes

def calculate_score(votes, storyteller, table):
    """
    Calculate the score for the round based on Dixit's scoring rules.
    
    Args:
        votes (List[int]): A list of player votes, where each vote is an index in `table`.
        storyteller (Player): The storyteller for the round.
        table (List[Tuple[int, str]]): A list of tuples containing player IDs and the chosen cards.
        
    Returns:
        int: The calculated score for the round.
    """
    try:
        storyteller_card_index = next(
            index for index, (player_id, card) in enumerate(table)
            if player_id == storyteller.player_id
        )
    except StopIteration:
        logger.error(f"Storyteller card not found in table. Table state: {table}")
        return 0

    correct_votes = votes.count(storyteller_card_index)
    total_votes = len(votes)

    if correct_votes == 0 or correct_votes == total_votes:
        score = -1
        logger.info(f"Storyteller {storyteller.name} failed to deceive players. No points awarded.")
    else:
        score = correct_votes * 2
        logger.info(f"Storyteller {storyteller.name} and {correct_votes} players scored.")

    for i, (player_id, card) in enumerate(table):
        if player_id != storyteller.player_id:
            deception_votes = votes.count(i)
            if deception_votes > 0:
                score += deception_votes
                logger.info(f"Player {player_id} deceived {deception_votes} players and scored.")

    return score
