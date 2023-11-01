



from functools import partial
from tkinter import *
from time import *
import threading
import random
import sys



"""

BIG NOTE!!! PRESS Q TO END GAME KISA DAAN KUN TERMINATE PROGRAM GA RUN MANGOD ANG GAME!!!
NO IDEA WHY!?

"""





# Global variable
whacks = 0
GAME_TIMER = 5
# Constant variables
HOLE_AMT = 6  # total holes is the square of this number
HOLE_PADDING = 1
BG_COLOR = "burlywood4"
LIGHT_COLOR = "#faead6"
DARK_COLOR = "#0c1703"
OTHER_COLOR = "#FF5733"





def start():
    global whacks, GAME_TIMER
    # Clear existing moles
    for i in range(len(hole)):
        hole[i].config(state="disabled")
    GAME_TIMER = 5
    whacks = 0
    scorelabel.config(text="0")
    timelabel.config(text=GAME_TIMER)
    remark.config(text="")

    t = threading.Thread(target=whac_a_mole)
    t.start()

def time():
    global GAME_TIMER
    while GAME_TIMER > 0:
        GAME_TIMER -= 1
        sleep(1)
        timelabel.config(text=GAME_TIMER)
        if GAME_TIMER == 0:
            handle_game_end()


def handle_game_end():
    global replaybtn
    replaybtn = Button(text=("Play Again"),font=("Stencil", 25), command=start, bg=BG_COLOR, fg=LIGHT_COLOR)


    replaybtn.place(x=0, y=0)


def reset_game():
    global replaybtn, whacks, GAME_TIMER
    replaybtn.place_forget()
    for i in range(len(hole)):
        hole[i].config(state="disabled")  # Disable all holes
    whacks = 0
    GAME_TIMER = 5
    start()



def ready_set_whack():
    sleep(1)
    scorelabel.config(text="Ready")
    sleep(1)
    scorelabel.config(text="Set")
    sleep(1)
    scorelabel.config(text="WHACK!!")
    sleep(1)
    scorelabel.config(text="0")


# Game!
def whac_a_mole():
    handle_game_end()
    #ready_set_whack()


    timer_thread = threading.Thread(target=time)
    timer_thread.start()

    mole = PhotoImage(file="mole.png")
    mole = mole.subsample(5)
    for i in range(0, 60):
        if GAME_TIMER == 0:  # Stop generating moles when the timer ends
            break
        hole_num = random.randint(0, HOLE_AMT**2 - 1)
        hole[hole_num].config(state="normal", image=mole)
        sleep(0.8)
        hole[hole_num].config(
            state="disabled", image=holepng, command=partial(onwhack, hole_num)
        )
    handle_game_end()
    # replaybtn.config(state='normal')

    # Give remark
    global whacks
    rating = {
        0: "POOR",
        10: "BAD",
        15: "DO BETTER!",
        20: "GOOD",
        25: "GREAT!",
        30: "AWESOME!",
        35: "WHACKED 'em ALL!",
    }
    for minscore, rm in rating.items():
        if whacks >= minscore and whacks < minscore + 10:
            remark.config(text=f"YOU DID \n {rm}", font=("Stencil", 50), bg=BG_COLOR, fg=LIGHT_COLOR)
            remark.placegrid(column=1, row=2)
            break


# When the mole is hit
def onwhack(num):
    hole[num].config(command=0, relief="sunken", image=hitpng)
    global whacks
    whacks += 1
    scorelabel.config(text="* " + str(whacks) + " *")




# Create window
screen = Tk()
screen.title("Shoot'eM ole")
screen.attributes("-fullscreen", True)
screen.config(bg=BG_COLOR)


# Title
title = Label(text="Shoot'eM ole", font=("Stencil", 50), bg=BG_COLOR, fg=LIGHT_COLOR)
title.grid(column=1, row=0, pady=10)

# Score
scorelabel = Label(
    text=whacks, width=9, font=("Cascadia Code", 30), bg=DARK_COLOR, fg=LIGHT_COLOR,
)
scorelabel.grid(column=1, row=1)


timelabel = Label(
    text=GAME_TIMER, width=9, font=("Cascadia Code", 30), bg=LIGHT_COLOR, fg=DARK_COLOR
)
timelabel.place(x=853, y=170)






# Remark
remark = Label(
    text="", width=17, bg=BG_COLOR, fg=BG_COLOR, font=("Ariel Rounded MT", 30)
)
remark.place(relx=0.15, rely=0.5, anchor=CENTER)
# remark.grid(column=1, row=3)


# Create playarea grid
playarea = Frame(screen, bg=BG_COLOR)
playarea.grid(column=1, row=2)
screen.columnconfigure(1, weight=1)
screen.rowconfigure(2, weight=1)


# Digging holes
hole = []
hole_index = 0
holepng = PhotoImage(file="hole.png")
holepng = holepng.subsample(5)
for row in range(HOLE_AMT):
    for col in range(HOLE_AMT):
        target = Button(
            playarea,
            image=holepng,
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

# Hit/whack effect
hitpng = PhotoImage(file="hit.png")
hitpng = hitpng.subsample(5)

# Pad holes
for child in playarea.winfo_children():
    child.grid_configure(padx=HOLE_PADDING, pady=HOLE_PADDING)





# waai ni pabayeh lng later on lng ni i edit in pre
"""
replaybtn = Button(text="Play Again", command=start)
replaybtn.place(x=0, y=2)
"""


# Press q to end game
def on_key(event):
    if event.char == "q":
        screen.destroy()
        sys.exit()


screen.bind("<Key>", on_key)


start()
screen.mainloop()
