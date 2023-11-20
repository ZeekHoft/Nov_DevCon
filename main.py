from functools import partial
from tkinter import *
from time import sleep
import threading
import random
import sys
from PIL import Image, ImageTk
import pyglet
import inputjoycon
import os
from pygame import mixer

pyglet.options["win32_gdi_font"] = True


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Global variable
points = 0
game_timer = 40
time_left = game_timer
rating = {
    0: "POORLY",
    5: "BADLY",
    10: "OKAY",
    15: "GOOD!",
    20: "GREAT!",
    25: "AMAZING",
    30: "AWESOME!",
    35: "EXCELLENT!",
}
difficulty = {
    "easy": (1, 1, 2, 1.5),
    "normal": (0.8, 0.8, 1.6, 0.98),
    "hard": (0.6, 0.7, 1.3, 0.9),
    "hardest": (0.4, 0.6, 1, 0.8),
}
currentdiff = difficulty["easy"]
jc, jc_thread, t = None, None, None

# Constant variables
GRID_AMT = 4  # total boxes is the square of this number
GRID_PAD = 10
LIGHT_COLOR = "#e0d6ff"
DARK_COLOR = "#2f373a"
PURPLE = "#0f0a21"


# Start or restart the game
def start(event):
    global t
    try:
        if t.is_alive():
            return
    except:
        pass
    global points, time_left
    for i in range(len(targets)):
        targets[i].config(state="disabled", image=blank, command=0)
    time_left = game_timer
    points = 0
    timelabel.config(text=f"{time_left} seconds")
    remark.grid_forget()

    t = threading.Thread(target=gameproper)
    t.start()


# Countdown timer
def time():
    global time_left
    while time_left > 0:
        time_left -= 1
        sleep(1)
        timelabel.config(text=f"{time_left} seconds")


# Ready the player
def ready_set_whack():
    sleep(1)
    scorelabel.config(text="Ready")
    sleep(1)

    scorelabel.config(text="Set")
    sleep(1)

    scorelabel.config(text="START!")
    sleep(1)
    scorelabel.config(text="0 points")


# Spawn a new entity in the target location
def new_entity(index):
    global points, currentdiff
    # Aswang
    if random.getrandbits(1):
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, True)
        )
        sleep(currentdiff[0])
        if not targets[index]["command"] == 0:
            targets[index].config(image=aswang)
        sleep(currentdiff[1])

    # Human
    else:
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, False)
        )
        sleep(currentdiff[2])
        # Add point if not hit
        if not targets[index]["command"] == 0:
            points += 1
            scorelabel.config(fg=LIGHT_COLOR)
            scorelabel.config(text=f"{points} points")

    targets[index].config(state="disabled", image=blank, command=0)


# Game!
def gameproper():
    ready_set_whack()

    timer_thread = threading.Thread(target=time)
    timer_thread.start()

    # Stop generating aswangs when the timer ends
    global points, currentdiff
    num_order = []
    highest = 0
    currentdiff = difficulty["easy"]
    while time_left:
        if points in list(rating.keys())[2::2] and points > highest:
            mixer.Sound.play(levelup)
            highest = points
        if time_left <= 10 and currentdiff == difficulty["hard"]:
            currentdiff = difficulty["hardest"]
            bglbl.config(image=bgred)
            for i in range(len(targets)):
                targets[i].config(bg="#e80042", activebackground="#e80042")
        elif time_left <= 20:
            currentdiff = difficulty["hard"]
        elif time_left <= 30:
            currentdiff = difficulty["normal"]
        index = random.randint(0, GRID_AMT**2 - 1)
        if index in num_order[-3:]:
            continue
        num_order.append(index)
        spawn_entity = threading.Thread(target=new_entity, args=(index,))
        spawn_entity.start()
        sleep(currentdiff[3])

    spawn_entity.join()

    # Give remark
    for minscore, rm in rating.items():
        if points >= minscore and points < minscore + 5:
            remark.config(text=f"You did\n{rm}")
            remark.grid(column=1, row=3)
            sleep(2)
            break
    for i in range(len(targets)):
        targets[i].config(bg=PURPLE, activebackground=PURPLE)
    bglbl.config(image=bgtk)
    timelabel.configure(text="Play Again")


# When the aswang/person is hit
def onwhack(index, if_aswang):
    global points
    if if_aswang:
        targets[index].config(command=0, relief="sunken", image=aswanghit)
        points += 1
        scorelabel.config(fg=LIGHT_COLOR)
        mixer.Sound.play(random.choice((ad1, ad2, ad3)))
    else:
        targets[index].config(command=0, relief="sunken", image=humanhit)
        points -= 1
        mixer.Sound.play(minus)
        scorelabel.config(fg="red")
    scorelabel.config(text=f"{points} points")


# Create window
screen = Tk()
screen.title("Aswang Busters")
screen.attributes("-fullscreen", True)
screen.config(cursor="@assets/cursor.cur")

# Background Image
bg = Image.open(resource_path("assets/background.png"))
width, height = screen.winfo_screenwidth(), screen.winfo_screenheight()
bgtk = ImageTk.PhotoImage(bg.resize((width, height)))
bglbl = Label(screen, image=bgtk, bg="black")
bglbl.place(x=0, y=0)
bgred = Image.open(resource_path("assets/backgroundred.png"))
bgred = ImageTk.PhotoImage(bgred.resize((width, height)))

pyglet.font.add_file(resource_path("assets/PixelDigivolve.ttf"))

# Title
title = Label(
    text="ASWANG BUSTERS", font=("Pixel Digivolve", 50), bg="#080513", fg=LIGHT_COLOR
)
title.grid(column=1, row=0, pady=10)
screen.rowconfigure(0, weight=1)

# Score
scorelabel = Label(
    text=points,
    width=11,
    font=("Pixel Digivolve", 30),
    bg=DARK_COLOR,
    fg=LIGHT_COLOR,
)
scorelabel.grid(column=1, row=1)
screen.rowconfigure(1, weight=1)

# Timer
timelabel = Label(
    text="Start", width=11, font=("Pixel Digivolve", 30), bg=LIGHT_COLOR, fg=DARK_COLOR
)
timelabel.bind(sequence="<Button-1>", func=start)
timelabel.grid(column=1, row=2)
screen.rowconfigure(2, weight=1)


# Create playarea grid
playarea = Label(screen, image=bgtk)
playarea.grid(column=1, row=3)
screen.columnconfigure(1, weight=1)
screen.rowconfigure(3, weight=10)
# Remark
remark = Label(text="", bg=PURPLE, fg=LIGHT_COLOR, font=("Pixel Digivolve", 50))

# Load all assets
ss = 4
blank = PhotoImage(file=resource_path("assets/blank.png")).subsample(ss)
human = PhotoImage(file=resource_path("assets/human.png")).subsample(ss)
humanhit = PhotoImage(file=resource_path("assets/humanhit.png")).subsample(ss)
aswang = PhotoImage(file=resource_path("assets/aswang.png")).subsample(ss)
aswanghit = PhotoImage(file=resource_path("assets/aswanghit.png")).subsample(ss)


targets = []
target_index = 0
for row in range(GRID_AMT):
    for col in range(GRID_AMT):
        target = Button(
            playarea,
            image=blank,
            bg=PURPLE,
            activebackground=PURPLE,
            border=0,
            command=0,
        )
        targets.append(target)
        targets[target_index].grid(column=col, row=row, sticky=NSEW)

        playarea.columnconfigure(col, weight=1)
        playarea.rowconfigure(row, weight=1)

        target_index += 1


# Space out the grid
for child in playarea.winfo_children():
    child.grid_configure(padx=GRID_PAD, pady=GRID_PAD)


# Press q to end game, space to start or calibrate joycon
# On joycon: r to calibrate
def on_key(event):
    global jc, jc_thread
    # If space is pressed
    if event.char == " ":
        # If joycon does not yet exist
        if jc == None:
            try:
                # Initiate and start joycon thread
                jc = inputjoycon.Joycon()
                jc.init_joycon()
                jc_thread = threading.Thread(target=jc.control_cursor)
                jc_thread.start()
            except:
                print("Connect joycon via Bluetooth first!")
        else:
            # Restart thread
            if not jc_thread.is_alive():
                jc_thread = None
                jc.init_joycon()
                jc_thread = threading.Thread(target=jc.control_cursor)
                jc_thread.start()
            # Calibrate
            else:
                jc.init_joycon()
    elif event.char == "q":
        try:
            jc.stop_joycon()
        except:
            pass
        screen.destroy()
        sys.exit()


screen.bind("<Key>", on_key)

# Music and Sounds
mixer.init()
mixer.music.load(resource_path("sounds/Leo Tirol - Just Survive.wav"))
mixer.music.set_volume(0.5)
mixer.music.play(-1)
levelup = mixer.Sound(resource_path("sounds/levelup.wav"))
bang = mixer.Sound(resource_path("sounds/shoot.wav"))
minus = mixer.Sound(resource_path("sounds/minus.wav"))
ad1 = mixer.Sound(resource_path("sounds/aswang death.wav"))
ad2 = mixer.Sound(resource_path("sounds/aswang death #2.wav"))
ad3 = mixer.Sound(resource_path("sounds/aswang death #3.wav"))


def shoot(event):
    mixer.Sound.play(bang)


screen.bind("<Button-1>", shoot)

screen.mainloop()
