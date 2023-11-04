from functools import partial
from tkinter import *
from time import *
import threading
import random
import sys
import pyttsx3


# Global variable
whacks = 0
game_timer = 20
time_left = game_timer

# Constant variables
HOLE_AMT = 4  # total holes is the square of this number
HOLE_PADDING = 10
BG_COLOR = "burlywood4"
LIGHT_COLOR = "#faead6"
DARK_COLOR = "#0c1703"
OTHER_COLOR = "#eff3a0"


# Start or reset the game
def start(event):
    global whacks, time_left
    for i in range(len(hole)):
        hole[i].config(state="disabled")
    time_left = game_timer
    whacks = 0
    timelabel.config(text=f"{time_left} seconds")
    remark.config(text="")

    t = threading.Thread(target=whac_a_mole)
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


def change_state(hole_num):
    hole[hole_num].config(image=holepng)
    sleep(1)
    hole[hole_num].config(state="normal", image=mole)
    sleep(1)
    hole[hole_num].config(
        state="disabled", image=blank, command=partial(onwhack, hole_num)
    )


# Game!
def whac_a_mole():
    ready_set_whack()

    timer_thread = threading.Thread(target=time)
    timer_thread.start()

    # Stop generating moles when the timer ends
    last_number = None
    while time_left:
        hole_num = random.randint(0, HOLE_AMT**2 - 1)
        if hole_num == last_number:
            continue
        last_number = hole_num
        change_hole = threading.Thread(target=change_state, args=(hole_num,))
        change_hole.start()
        sleep(0.8)

    change_hole.join()
    timelabel.configure(text="Play Again")

    # Give remark
    global whacks
    rating = {
        0: "POORLY",
        10: "BADLY",
        20: "WELL!",
        30: "GOOD",
        40: "GREAT!",
        50: "AWESOME!",
        60: "WHACKED 'em ALL!",
    }
    for minscore, rm in rating.items():
        if whacks >= minscore and whacks < minscore + 10:
            remark.config(text=f"You did\n{rm}", fg=LIGHT_COLOR)
            engine.say(f"You did {rm}")
            engine.runAndWait()
            break


# When the mole is hit
def onwhack(num):
    hole[num].config(command=0, relief="sunken", image=hitpng)
    global whacks
    whacks += 1
    scorelabel.config(text=f"{whacks} points")


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
title = Label(text="Shoot'eM ole", font=("Stencil", 50), bg=BG_COLOR, fg=LIGHT_COLOR)
title.grid(column=1, row=0, pady=10)
screen.rowconfigure(0, weight=1)

# Score
scorelabel = Label(
    text=whacks,
    width=11,
    font=("Cascadia Code", 30),
    bg=DARK_COLOR,
    fg=LIGHT_COLOR,
)
scorelabel.grid(column=1, row=1)
screen.rowconfigure(1, weight=1)

timelabel = Label(
    text="Start", width=11, font=("Cascadia Code", 30), bg=LIGHT_COLOR, fg=DARK_COLOR
)
timelabel.bind(sequence="<Button-1>", func=start)
timelabel.grid(column=1, row=2)
screen.rowconfigure(2, weight=1)

# Remark
remark = Label(text="", width=17, bg=BG_COLOR, fg=BG_COLOR, font=("Stencil", 50))
remark.place(relx=0.15, rely=0.5, anchor=CENTER)
# remark.grid(column=1, row=3)


# Create playarea grid
playarea = Frame(screen, bg=BG_COLOR)
playarea.grid(column=1, row=3)
screen.columnconfigure(1, weight=1)
screen.rowconfigure(3, weight=7)


# Load all assets
holepng = PhotoImage(file="hole.png").subsample(5)
blank = PhotoImage(file="blank.png").subsample(5)
mole = PhotoImage(file="mole.png").subsample(5)
hitpng = PhotoImage(file="hit.png").subsample(5)


hole = []
hole_index = 0
for row in range(HOLE_AMT):
    for col in range(HOLE_AMT):
        target = Button(
            playarea,
            image=blank,
            bg=BG_COLOR,
            state="disabled",
            activebackground=BG_COLOR,
            border=0,
            command=partial(onwhack, hole_index),
        )
        hole.append(target)
        hole[hole_index].grid(column=col, row=row, sticky=NSEW)

        playarea.columnconfigure(col, weight=1)
        playarea.rowconfigure(row, weight=1)

        hole_index += 1


# Pad holes
for child in playarea.winfo_children():
    child.grid_configure(padx=HOLE_PADDING, pady=HOLE_PADDING)


# Press q to end game
def on_key(event):
    if event.char == "q":
        screen.destroy()
        sys.exit()


screen.bind("<Key>", on_key)


screen.mainloop()
