import ctypes
import pyautogui  # For image recognition only
import pydirectinput  # For keyboard input
import time
import sys
import os
import logging
import keyboard  # For script control
from pathlib import Path


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


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


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logger.info(f"Running in PyInstaller bundle. Base path: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        logger.info(f"Running as script. Base path: {base_path}")

    full_path = os.path.join(base_path, relative_path)
    logger.info(f"Resource path for '{relative_path}': {full_path}")
    return full_path


def setup():
    """Initialize and find the button image"""
    logger.info("Starting setup")

    # Try multiple potential locations for the image
    potential_paths = [
        resource_path("play_again_button.png"),
        os.path.abspath("play_again_button.png"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "play_again_button.png"),
        os.path.join(os.getcwd(), "play_again_button.png")
    ]

    # Log all files in current directory and _MEIPASS if it exists
    try:
        logger.info(f"Files in current directory: {os.listdir(os.getcwd())}")
        if hasattr(sys, '_MEIPASS'):
            logger.info(f"Files in _MEIPASS: {os.listdir(sys._MEIPASS)}")
    except Exception as e:
        logger.error(f"Error listing directory contents: {e}")

    # Try each path
    button_path = None
    for path in potential_paths:
        try:
            if os.path.exists(path):
                button_path = path
                logger.info(f"Found button image at: {button_path}")
                break
        except Exception as e:
            logger.error(f"Error checking path {path}: {e}")

    if button_path is None:
        logger.error("Could not find 'play_again_button.png' in any location")
        print("Error: Cannot find 'play_again_button.png'. Please ensure the screenshot file is in the same directory.")
        print("Checked paths:")
        for path in potential_paths:
            print(f" - {path}")
        return False, None

    print(f"Found button image: {button_path}")
    return True, button_path


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
        logger.info(f"Looking for button using image path: {image_path}")
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
    setup_result = setup()

    if isinstance(setup_result, tuple) and len(setup_result) == 2:
        success, button_path = setup_result
        if not success:
            input("Press Enter to exit...")
            return
    else:
        logger.error(f"Unexpected setup result: {setup_result}")
        print("An error occurred during setup.")
        input("Press Enter to exit...")
        return

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
            if find_and_click_button(button_path):
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
        input("Press Enter to exit...")


if __name__ == "__main__":
    print("=== Auto Play Again Script ===")
    print("Starting up...")
    main_loop()
    print("Script has ended.")
    time.sleep(1)
