from functools import partial
from tkinter import *
from time import *
import threading
import random
import sys
import pyttsx3


# Global variable
points = 0
game_timer = 20
time_left = game_timer
rating = {
    0: "POORLY",
    10: "BADLY",
    20: "WELL!",
    30: "GOOD",
    40: "GREAT!",
    50: "AWESOME!",
    60: "WHACKED 'em ALL!",
}

# Constant variables
GRID_AMT = 4  # total boxes is the square of this number
GRID_PAD = 10
BG_COLOR = "#f4f5f6"
DARK_COLOR = "#2f3237"
GREY_COLOR = "#d6d8db"


# Start or restart the game
def start(event):
    global points, time_left
    # for i in range(len(targets)):
    #     targets[i].config(state="disabled")
    time_left = game_timer
    points = 0
    timelabel.config(text=f"{time_left} seconds")
    remark.config(text="")

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
    engine.say("Ready")
    engine.runAndWait()

    scorelabel.config(text="Set")
    engine.say("Set")
    engine.runAndWait()

    scorelabel.config(text="WHACK!!")
    engine.say("WHACK!!")
    engine.runAndWait()
    scorelabel.config(text="0 points")


# Spawn a new entity in the target location
def new_entity(index):
    # Aswang
    if random.getrandbits(1):
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, True)
        )
        sleep(1)
        if not targets[index]["command"] == 0:
            targets[index].config(image=aswang)

    # Human
    else:
        targets[index].config(
            image=human, state="active", command=partial(onwhack, index, False)
        )

    sleep(2)
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
        sleep(1.3)

    spawn_entity.join()

    # Give remark
    global points
    for minscore, rm in rating.items():
        if points >= minscore and points < minscore + 10:
            remark.config(text=f"You did\n{rm}", fg=DARK_COLOR)
            engine.say(f"You did {rm}")
            engine.runAndWait()
            break

    timelabel.configure(text="Play Again")


# When the aswang is hit
def onwhack(index, if_aswang):
    global points
    if if_aswang:
        targets[index].config(command=0, relief="sunken", image=aswanghit)
        points += 1
    else:
        targets[index].config(command=0, relief="sunken", image=humanhit)
        points -= 1
    scorelabel.config(text=f"{points} points")


# Text to speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 130)
engine.setProperty("volume", 1)


# Create window
screen = Tk()
screen.title("Shoot'eM ole")
screen.attributes("-fullscreen", True)
screen.config(bg=BG_COLOR)


# Title
title = Label(
    text="Aswang Game (tentative)", font=("Chiller", 50), bg=BG_COLOR, fg=DARK_COLOR
)
title.grid(column=1, row=0, pady=10)
screen.rowconfigure(0, weight=1)

# Score
scorelabel = Label(
    text=points,
    width=11,
    font=("Cascadia Code", 30),
    bg=DARK_COLOR,
    fg=BG_COLOR,
)
scorelabel.grid(column=1, row=1)
screen.rowconfigure(1, weight=1)

timelabel = Label(
    text="Start", width=11, font=("Cascadia Code", 30), bg=BG_COLOR, fg=DARK_COLOR
)
timelabel.bind(sequence="<Button-1>", func=start)
timelabel.grid(column=1, row=2)
screen.rowconfigure(2, weight=1)

# Remark
remark = Label(text="", width=17, bg=BG_COLOR, fg=BG_COLOR, font=("Stencil", 50))
remark.place(relx=0.15, rely=0.5, anchor=CENTER)
# remark.grid(column=1, row=3)


# Create playarea grid
playarea = Frame(screen, bg=GREY_COLOR)
playarea.grid(column=1, row=3)
screen.columnconfigure(1, weight=1)
screen.rowconfigure(3, weight=7)


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
            bg=GREY_COLOR,
            activebackground=GREY_COLOR,
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


# Press q to end game
def on_key(event):
    if event.char == "q":
        screen.destroy()
        sys.exit()


screen.bind("<Key>", on_key)


screen.mainloop()
