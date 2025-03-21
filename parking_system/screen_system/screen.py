import json
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

    try:
        decoded_json = json.loads(message.decode())
        state_code = str(decoded_json.get("state_code", ""))
        plate = decoded_json.get("plate", "")

        # Solo actualiza si el código es válido
        if state_code in BaseConfig.SCREEN_MESSAGES:
            template = BaseConfig.SCREEN_MESSAGES[state_code]
            current_status = template.format(plate=plate)
        else:
            # Código no reconocido: no cambiar current_status
            pass

    except Exception:
        # Error en el mensaje: no cambiar current_status
        pass


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


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        # Try to add the word to the current line
        test_line = current_line + (" " if current_line else "") + word
        test_surface = font.render(test_line, True, (255, 255, 255))
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            # If the word doesn't fit, start a new line
            if current_line:
                lines.append(current_line)
            current_line = word
    
    # Add the last line
    if current_line:
        lines.append(current_line)

    return lines


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

        # Wrap the text and render each line
        lines = wrap_text(current_status, font, width - 40)  # 40px padding

        # Calculate the total height of all lines
        total_text_height = sum(font.get_height() for _ in lines) + (len(lines) - 1) * 5  # spacing between lines

        # Start drawing the wrapped text in the vertical center
        y_offset = (height - total_text_height) // 2  # Start in the middle of the screen

        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += font.get_height() + 5  # Adjust vertical spacing between lines

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
