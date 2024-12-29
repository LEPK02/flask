import logging

logging.basicConfig(
    filename='app.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-4s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger()