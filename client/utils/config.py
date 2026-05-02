import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [CLIENT] - %(message)s',
        handlers=[
            logging.FileHandler("client_logs.log"),
            logging.StreamHandler()
        ]
    )