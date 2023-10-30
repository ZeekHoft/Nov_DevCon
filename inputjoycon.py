from pyjoycon import get_R_id, GyroTrackingJoyCon, ButtonEventJoyCon
import pyautogui
import ctypes #For get resolution of the screen
import math

class MyJoyCon(GyroTrackingJoyCon, ButtonEventJoyCon):
    pass

joycon_id = get_R_id()
joycon = MyJoyCon(*joycon_id)

print(joycon.get_status())


def test_joycon():

    # joycon pointer coordinates
    joyconcoords = [joycon.pointer[0] * 100, joycon.pointer[1] * 100]

    #x and y cordinates are divided by two to fall in the center of the screen (for any monitor)
    center_res = ctypes.windll.user32.GetSystemMetrics(0)/2, ctypes.windll.user32.GetSystemMetrics(1)/2

    # Convert normalized coordinates to screen coordinates
    screen_width, screen_height = pyautogui.size()
    print(screen_width)
    
    # Calculate the center of the screen
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Map normalized coordinates to screen coordinates starting from the center
    screen_x = int(center_x + joycon.pointer[0] * center_x)
    screen_y = int(center_y + joycon.pointer[1] * center_y)
    pyautogui.moveTo(center_res)

    # Define the sensitivity for cursor movement
    max_sensitivity = 20  # Maximum sensitivity
    min_sensitivity = 5   # Minimum sensitivity
    max_distance = math.sqrt(center_x**2 + center_y**2)  # Maximum distance from the center

    # Define the weight for smoothing (between 0 and 1)
    smoothing_weight = 0.8  # Adjust as needed

    # updated 21/10/23
    # Define the dead zone size (adjust as needed)
    dead_zone_size = 5  # Adjust this value based on your Joy-Con's behavior

    # Define grid parameters (adjust as needed)
    grid_size = 50  # Size of each grid cell in pixels
    snap_distance = 20  # Distance at which cursor snaps to the grid

    while True:
        # joycon pointer coordinates
        joyconcoords = [joycon.pointer[0] * 100, joycon.pointer[1] * 100]

        # Calculate the displacement from the center
        distance_from_center = math.sqrt((joyconcoords[0]*center_x)**2 + (joyconcoords[1]*center_y)**2)

        # Apply a dead zone to the gyroscope data
        if distance_from_center < dead_zone_size:
            joyconcoords = [0, 0]

        sensitivity = min(max_sensitivity, max(min_sensitivity, distance_from_center / max_distance * max_sensitivity))

        # Calculate cursor displacement based on gyroscope data
        displacement_x = joyconcoords[0] * sensitivity
        displacement_y = -joyconcoords[1] * sensitivity  # Invert the Y-axis

        # Calculate the target cursor position
        target_x = round(center_x + displacement_x, 2)
        target_y = round(center_y + displacement_y, 2)

        # Get the current cursor position
        current_x, current_y = pyautogui.position()

        # Check if the cursor is close to a grid cell
        if abs(target_x % grid_size) < snap_distance:
            target_x = round(target_x / grid_size) * grid_size
        if abs(target_y % grid_size) < snap_distance:
            target_y = round(target_y / grid_size) * grid_size

        # Apply smoothing to the target position
        smoothed_x = smoothing_weight * target_x + (1 - smoothing_weight) * current_x
        smoothed_y = smoothing_weight * target_y + (1 - smoothing_weight) * current_y

        # Move the mouse to the smoothed position
        pyautogui.moveTo(smoothed_x, smoothed_y)

        for event_type, status in joycon.events():
            if event_type == "zr" and status == True:

                # printing joyconcoords
                print("\njoyconcoords:")
                print(f"x: {joyconcoords[0]}")
                print(f"x: {joyconcoords[1]}")
                print(f"bang lol")
                pyautogui.click()


test_joycon()   