import logging
import logging.config
from logging.handlers import RotatingFileHandler

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': 'logs/dixit_game.log',
            'maxBytes': 5 * 1024 * 1024,  
            'backupCount': 5, 
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'game_logic': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'data_collection': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'clue_generation': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)