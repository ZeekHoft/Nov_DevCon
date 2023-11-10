from functools import partial
from tkinter import *
from time import *
import threading
import random
import sys
from PIL import Image, ImageTk
import pyglet
import inputjoycon

pyglet.options["win32_gdi_font"] = True

# Global variable
points = 0
game_timer = 30
time_left = game_timer
rating = {
    0: "POORLY",
    5: "BADLY",
    10: "WELL!",
    15: "GOOD!",
    20: "GREAT!",
    25: "AWESOME!",
}

# Constant variables
GRID_AMT = 4  # total boxes is the square of this number
GRID_PAD = 10
LIGHT_COLOR = "#e0d6ff"
DARK_COLOR = "#2f373a"
PURPLE = "#0f0a21"


# Start or restart the game
def start(event):
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
    global points
    # Aswang
    if random.getrandbits(1):
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, True)
        )
        sleep(0.8)
        if not targets[index]["command"] == 0:
            targets[index].config(image=aswang)
        sleep(0.8)

    # Human
    else:
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, False)
        )
        sleep(1.6)
        # Add point if not hit
        if not targets[index]["command"] == 0:
            points += 1
            scorelabel.config(text=f"{points} points")

    targets[index].config(state="disabled", image=blank, command=0)


# Game!
def gameproper():
    ready_set_whack()

    timer_thread = threading.Thread(target=time)
    timer_thread.start()

    # Stop generating aswangs when the timer ends
    num_order = []
    while time_left:
        index = random.randint(0, GRID_AMT**2 - 1)
        if index in num_order[-3:]:
            continue
        num_order.append(index)
        spawn_entity = threading.Thread(target=new_entity, args=(index,))
        spawn_entity.start()
        sleep(1)

    spawn_entity.join()

    # Give remark
    global points
    for minscore, rm in rating.items():
        if points >= minscore and points < minscore + 5:
            remark.config(text=f"You did\n{rm}")
            remark.grid(column=1, row=3)
            sleep(2)
            break
    timelabel.configure(text="Play Again")


# When the aswang/person is hit
def onwhack(index, if_aswang):
    global points
    if if_aswang:
        targets[index].config(command=0, relief="sunken", image=aswanghit)
        points += 1
    else:
        targets[index].config(command=0, relief="sunken", image=humanhit)
        points -= 1
    scorelabel.config(text=f"{points} points")


# Create window
screen = Tk()
screen.title("Aswang Busters")
screen.attributes("-fullscreen", True)
screen.config(cursor="@./assets/cursor.cur")

# Background Image
bg = Image.open("./assets/background.png")
width, height = screen.winfo_screenwidth(), screen.winfo_screenheight()
bg = ImageTk.PhotoImage(bg.resize((width, height)))
bglbl = Label(screen, image=bg, bg="black")
bglbl.place(x=0, y=0)

pyglet.font.add_file("./assets/PixelDigivolve.ttf")

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
image_path = "./assets/background.png"
transparent_image = PhotoImage(file=image_path)
playarea = Label(screen, image=transparent_image)
playarea.grid(column=1, row=3)
playarea.image = transparent_image
screen.columnconfigure(1, weight=1)
screen.rowconfigure(3, weight=7)
# Remark
remark = Label(text="", bg=PURPLE, fg=LIGHT_COLOR, font=("Pixel Digivolve", 50))

# Load all assets
blank = PhotoImage(file="./assets/blank.png").subsample(5)
human = PhotoImage(file="./assets/human.png").subsample(5)
humanhit = PhotoImage(file="./assets/humanhit.png").subsample(5)
aswang = PhotoImage(file="./assets/aswang.png").subsample(5)
aswanghit = PhotoImage(file="./assets/aswanghit.png").subsample(5)


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


# Press q to end game, j to activate joycon
def on_key(event):
    if event.char == "q":
        screen.destroy()
        sys.exit()
    if event.char == "j":
        try:
            inputjoycon.activate_joycon()
        except:
            print("Connect joycon via Bluetooth first!")


screen.bind("<Key>", on_key)


screen.mainloop()
