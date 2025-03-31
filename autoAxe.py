import ctypes
import pyautogui  # For image recognition only
import pydirectinput  # For keyboard input
import time
import os
import logging
import keyboard  # For script control
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='auto_play.log')
logger = logging.getLogger()

# Win32 API constants for mouse
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Configure pydirectinput
pydirectinput.PAUSE = 0.1  # Add a small pause between actions

# Load user32.dll
user32 = ctypes.windll.user32


def setup():
    """Initialize settings and check for required files"""
    logger.info(
        "Starting hybrid automation script: Win32 mouse + PyDirectInput keyboard")

    # Check if the play again button screenshot exists
    button_path = Path("play_again_button.png")
    if not button_path.exists():
        logger.error(
            f"Cannot find 'play_again_button.png'. Please ensure the screenshot file is in the same directory.")
        print(f"Error: Cannot find 'play_again_button.png'. Please ensure the screenshot file is in the same directory.")
        return False

    logger.info(f"Found button image: {button_path.absolute()}")
    return True


def find_and_click_button(image_path, confidence=0.7):
    """
    Find using PyAutoGUI but click using Win32 API

    Args:
        image_path: Path to the button image
        confidence: Confidence level for image matching (0-1)

    Returns:
        bool: Whether the button was successfully found and clicked
    """
    try:
        # Look for the button on screen
        button_location = pyautogui.locateOnScreen(
            image_path, confidence=confidence, grayscale=True)

        if button_location:
            # Calculate the center of the button
            button_center = pyautogui.center(button_location)

            # Move cursor to position
            user32.SetCursorPos(int(button_center.x), int(button_center.y))

            # Perform mouse click using Win32 API
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

            # Double-click for reliability
            time.sleep(0.1)
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

            logger.info(f"Successfully clicked button at: {button_center}")
            return True
        else:
            logger.info("Button not found")
            return False

    except Exception as e:
        logger.error(f"Error finding button: {str(e)}")
        return False


def press_x_key(duration=0.5):
    """
    Press and hold the X key using PyDirectInput

    Args:
        duration: Key press duration in seconds
    """
    logger.info(f"Pressing X key for {duration} seconds using PyDirectInput")

    # Press and hold X key using PyDirectInput
    pydirectinput.keyDown('x')
    time.sleep(duration)
    pydirectinput.keyUp('x')

    logger.info("Released X key")


def main_loop():
    """Main loop to find and click the play again button, pressing X when necessary"""
    if not setup():
        return

    button_image = "play_again_button.png"

    print("Script is running. Press 'Q' to exit.")

    try:
        while True:
            # Check for Q key press to exit
            if keyboard.is_pressed('q'):
                logger.info("User pressed Q key, exiting script")
                print("\nQ key pressed. Script stopped.")
                return

            print("Looking for 'Play Again' button...")

            # Try to find and click the button
            if find_and_click_button(button_image):
                print("Found and clicked 'Play Again' button!")
                # Wait for game to load, adjust time as needed
                time.sleep(0.5)
            else:
                print("Button not found, pressing X for 0.5 seconds...")
                # If button not found, press X key using PyDirectInput
                press_x_key(0.5)
                # Wait briefly before trying again
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        print("\nScript stopped.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main_loop()
