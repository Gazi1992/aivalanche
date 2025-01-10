import logging

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'filename': 'default.log',  # Initial path, will be updated
            'formatter': 'standard',
            'level': 'DEBUG',
        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['file_handler', 'console_handler'],
        'level': 'DEBUG',
    },
}

def set_log_file(config: dict = {}, path: str = ''):
    for handler in config.get('handlers', {}).values():
        if handler.get('class') == 'logging.FileHandler':
            handler['filename'] = path
    logging.config.dictConfig(config)
            
def set_log_level(config: dict = {}, level: str = 'DEBUG'):
    for handler in config.get('handlers', {}).values():
        handler['level'] = level
    logging.config.dictConfig(config)

