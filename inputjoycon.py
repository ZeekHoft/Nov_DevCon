from pyjoycon import get_R_id, GyroTrackingJoyCon, ButtonEventJoyCon
import pyautogui
import ctypes  # For get resolution of the screen
import math

pyautogui.FAILSAFE = False


class MyJoyCon(GyroTrackingJoyCon, ButtonEventJoyCon):
    pass


class Joycon:
    stop = False

    def init_joycon(self):
        joycon_id = get_R_id()
        self.joycon = MyJoyCon(*joycon_id)
        # joycon pointer coordinates
        self.joyconcoords = [self.joycon.pointer[0] * 100, self.joycon.pointer[1] * 100]

        # x and y cordinates are divided by two to fall in the center of the screen (for any monitor)
        center_res = (
            ctypes.windll.user32.GetSystemMetrics(0) / 2,
            ctypes.windll.user32.GetSystemMetrics(1) / 2,
        )

        # Convert normalized coordinates to screen coordinates
        screen_width, screen_height = pyautogui.size()

        # Calculate the center of the screen
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

        # Map normalized coordinates to screen coordinates starting from the center
        pyautogui.moveTo(center_res)

        # Define the sensitivity for cursor movement
        self.max_sensitivity = 20  # Maximum sensitivity
        self.min_sensitivity = 5  # Minimum sensitivity
        self.max_distance = math.sqrt(
            self.center_x**2 + self.center_y**2
        )  # Maximum distance from the center

    def control_cursor(self):
        while True:
            if self.stop:
                return

            # joycon pointer coordinates
            joyconcoords = [self.joycon.pointer[0] * 100, self.joycon.pointer[1] * 100]

            # Calculate the displacement from the center
            distance_from_center = math.sqrt(
                (joyconcoords[0] * self.center_x) ** 2
                + (joyconcoords[1] * self.center_y) ** 2
            )

            sensitivity = min(
                self.max_sensitivity,
                max(
                    self.min_sensitivity,
                    distance_from_center / self.max_distance * self.max_sensitivity,
                ),
            )

            # Calculate cursor displacement based on gyroscope data
            displacement_x = joyconcoords[0] * sensitivity
            displacement_y = -joyconcoords[1] * sensitivity  # Invert the Y-axis

            # Calculate the target cursor position
            target_x = round(self.center_x + displacement_x, 2)
            target_y = round(self.center_y + displacement_y, 2)

            # Move the mouse to the smoothed position
            pyautogui.moveTo(target_x, target_y, _pause=False)

            for event_type, status in self.joycon.events():
                if event_type == "zr" and status == True:
                    # printing joyconcoords
                    """
                    print("\njoyconcoords:")
                    print(f"x: {joyconcoords[0]}")
                    print(f"x: {joyconcoords[1]}")
                    print(f"bang lol")
                    """
                    pyautogui.click()

                # Press x to calibrate/reset
                elif event_type == "x" and status == True:
                    self.init_joycon()

                elif event_type == "b" and status == True:
                    self.stop = True

    def stop_joycon(self):
        self.stop = True
