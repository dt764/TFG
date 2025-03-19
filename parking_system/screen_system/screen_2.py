import pygame
import threading
import os
import sys

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from parking_system.base_config import BaseConfig
from parking_system.communication.mqtt_msg import MQTT_Msg_Disp
from logging_module.logger_setup import setup_logger

current_status = "Esperando a sistema de detección..."


def handle_message_update(message):
    global current_status
    decoded_message = message.decode()
    current_status = decoded_message


def mqtt_thread():
    msg_dispatcher = MQTT_Msg_Disp(
        hostname=BaseConfig.MQTT_BROKER_URL,
        port=BaseConfig.MQTT_BROKER_PORT,
        publish_topic=None,
        sub_topic=BaseConfig.SCREEN_QUEUE_NAME,
        on_message_callback=handle_message_update,
        stop_consuming_after_received_message=False
    )
    msg_dispatcher.wait_and_receive_msg()


def main():
    global current_status

    setup_logger()

    threading.Thread(target=mqtt_thread, daemon=True).start()

    pygame.init()

    # Create screen
    screen_width = 800
    screen_height = 400
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Parking Status Screen")

    # Function to get responsive font size
    def get_font(width, height):
        size = min(width, height) // 8  # adjust divisor to your liking
        return pygame.font.SysFont("Arial", size)

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((30, 30, 30))
        width, height = screen.get_size()
        font = get_font(width, height)

        text_surface = font.render(current_status, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
