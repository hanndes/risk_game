import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [SERVER] - %(message)s',
        handlers=[
            logging.FileHandler("server_logs.log"),
            logging.StreamHandler()
        ]
    )