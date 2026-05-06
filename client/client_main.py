import logging

from client_controller import ClientController

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    controller = ClientController()
    controller.run()

if __name__ == "__main__":
    main()

