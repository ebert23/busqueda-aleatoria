import pyautogui
import cv2
import numpy as np
import time
from typing import Tuple
from pynput import keyboard

# Configure PyAutoGUI settings
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1  # Add small delay between actions

class RandomElementClicker:
    def __init__(self):
        self.original_position = (0, 0)
        self.screen_width, self.screen_height = pyautogui.size()
        self.is_active = False
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    
    def on_press(self, key):
        """Handle keyboard events"""
        try:
            if key == keyboard.Key.space:
                self.is_active = not self.is_active
                status = "activated" if self.is_active else "deactivated"
                print(f"\nClicker {status}")
        except AttributeError:
            pass
    
    def save_current_position(self) -> None:
        """Save the current mouse position"""
        self.original_position = pyautogui.position()
    
    def return_to_original_position(self) -> None:
        """Return to the saved position"""
        pyautogui.moveTo(*self.original_position)
    
    def find_element_on_screen(self) -> Tuple[int, int] | None:
        """Take a screenshot and find a specific element"""
        # Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Define the color range to detect (example: bright red elements)
        lower_color = np.array([0, 100, 100])
        upper_color = np.array([10, 255, 255])
        
        # Create a mask for the specified color range
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # If any contour is found, return the center of the largest one
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                return (cx, cy)
        return None
    
    def click_element(self, position: Tuple[int, int]) -> None:
        """Move to the specified position and click"""
        pyautogui.moveTo(position[0], position[1], duration=0.5)
        pyautogui.click()
    
    def run(self):
        """Main loop to find and click elements"""
        print("Starting Random Element Clicker...")
        print("Press SPACE to toggle clicker on/off")
        print("Move mouse to the corner of the screen to stop")
        
        while True:
            try:
                if self.is_active:
                    # Save current position
                    self.save_current_position()
                    
                    # Look for element
                    element_pos = self.find_element_on_screen()
                    
                    if element_pos:
                        # Click the element
                        self.click_element(element_pos)
                        # Wait a moment
                        time.sleep(0.5)
                        # Return to original position
                        self.return_to_original_position()
                
                # Small delay before next iteration
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
        
        # Clean up
        self.listener.stop()

if __name__ == "__main__":
    clicker = RandomElementClicker()
    clicker.run()