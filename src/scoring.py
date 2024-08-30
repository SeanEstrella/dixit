import logging

logger = logging.getLogger('game_logic')

def score_clue_performance(votes, storyteller_id):
    """
    Evaluate the performance of the clue based on voting results.

    Args:
        votes (list): List of player votes where each vote is the player ID guessed.
        storyteller_id (int): The ID of the storyteller.

    Returns:
        int: Performance score (-1 for too easy/hard, 1 for balanced, 0 for others).
    """
    correct_votes = sum(1 for vote in votes if vote == storyteller_id)
    total_players = len(votes)

    if correct_votes == 0 or correct_votes == total_players - 1:
        logger.info(f"Score -1: Clue was too easy or too difficult. Correct votes: {correct_votes}, Total players: {total_players}")
        return -1 
    elif 1 <= correct_votes < total_players - 1:
        logger.info(f"Score 1: Clue was well-balanced. Correct votes: {correct_votes}, Total players: {total_players}")
        return 1
    else:
        logger.info(f"Score 0: Neutral score. Correct votes: {correct_votes}, Total players: {total_players}")
        return 0

def adjust_generation_parameters(score, current_temperature):
    """
    Adjust the temperature parameter for clue generation based on performance.

    Args:
        score (int): Performance score from -1 to 1.
        current_temperature (float): The current temperature value.

    Returns:
        float: New adjusted temperature value.
    """
    current_temperature = max(0.7, min(current_temperature, 1.0))

    if score == -1:
        new_temperature = min(current_temperature + 0.1, 1.0)
    elif score == 1:
        new_temperature = max(current_temperature - 0.05, 0.7)
    else:
        new_temperature = current_temperature

    logger.info(f"Adjusting temperature: {current_temperature} -> {new_temperature}")
    return new_temperature
