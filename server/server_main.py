from server.tcp_server import RiskServer
import time
import logging

if __name__ == "__main__":
    server = RiskServer()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("[MAIN] Sunucu kullanıcı tarafından kapatılıyor...")
        server.stop()