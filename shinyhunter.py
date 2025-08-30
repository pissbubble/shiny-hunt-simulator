import requests
import random
import asyncio
from time import sleep
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Shiny Hunting Simulator")


frm = ttk.Frame(root, padding=10)
frm.grid()

# Label for odds
odds_label = ttk.Label(frm, text="odds?")
odds_label.grid(column=0, row=0)

# Entry box for user input
odds_entry = ttk.Entry(frm)
odds_entry.grid(column=1, row=0)

# Label for cooldown
cd_label = ttk.Label(frm, text="cooldown? (seconds)")
cd_label.grid(column=0, row=1)

# Entry box for user input
cd_entry = ttk.Entry(frm)
cd_entry.grid(column=1, row=1)

#text output
result_label = ttk.Label(frm, text="")
result_label.grid(column=1, row=10)

def encounter():
    try:
        cooldown = int(cd_entry.get()) * 1000 # read number from entry


    except ValueError:
        cooldown = 3000
        

    # disable button for cooldown
    btn.config(state=DISABLED)
    root.after(cooldown, lambda: btn.config(state=NORMAL))  # 1000 ms = 1 second


    try:
        odds = int(odds_entry.get())  # read number from entry

    except ValueError:
        odds = 20

    shiny = random.randint(1,odds)

    result = "shiny" if shiny == 1 else "regular ass"

    result_label.config(text=result)

btn = ttk.Button(frm, text="Encounter!", command=lambda: encounter())
btn.grid(column=0, row=10)

root.mainloop()