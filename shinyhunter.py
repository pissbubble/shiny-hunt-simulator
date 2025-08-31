import os, sys
import requests
import random
from io import BytesIO
from PIL import Image as pimage, ImageTk
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font



def resource_path(relative_path):
    """Get path whether running as script or PyInstaller exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        # create a small popup near the widget
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # no border, title bar, etc.
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, background="lightyellow",
            relief="solid", borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def add_placeholder(entry, placeholder, color="grey"):
    normal_fg = entry.cget("foreground")

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(foreground=normal_fg)

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground=color)

    # Set initial placeholder
    entry.insert(0, placeholder)
    entry.config(foreground=color)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


root = Tk()
root.title("Shiny Hunting Simulator")
root.iconbitmap(resource_path("images/shinyhuntsim.ico"))

root.attributes("-fullscreen", False)
root.resizable(False, False)

big_font = font.Font(family="Arial", size=14)
reg_font = font.Font(family="Arial", size=12)
root.option_add("*TButton.Font", big_font)
root.option_add("*TLabel.Font", big_font)
root.option_add("*TEntry.Font", big_font)

# frame and grid for prompts and buttons
frm_left = ttk.Frame(root, padding=10)
frm_left.grid(column=0, row=0)

# frame for pokemon image
frm_right = ttk.Frame(root, padding=10)
frm_right.grid(column=1, row=0)

# Label for pokemon field
pkmn_label = ttk.Label(frm_left, text="Pokemon?")
pkmn_label.grid(column=0, row=0)

# Entry box for pokemon input
pkmn_entry = ttk.Entry(frm_left)
pkmn_entry.grid(column=1, row=0)
add_placeholder(pkmn_entry, "name or dex number")

# Label for odds field
odds_label = ttk.Label(frm_left, text="Odds?")
odds_label.grid(column=0, row=1)

# Entry box for odds input
odds_entry = ttk.Entry(frm_left)
odds_entry.grid(column=1, row=1)
add_placeholder(odds_entry, "e.g. 8192 for 1/8192")

img = pimage.open(resource_path("images/info.png"))   # path to your downloaded icon
img = img.resize((16, 16), pimage.Resampling.LANCZOS)
info_icon = ImageTk.PhotoImage(img)

info_label = ttk.Label(frm_left, image=info_icon)
info_label.grid(column=2, row=1)
ToolTip(info_label, "Leave blank for full odds, relative to the Pokemon's home generation.")

# Label for cooldown field
cd_label = ttk.Label(frm_left, text="Cooldown?")
cd_label.grid(column=0, row=2)

# Entry box for cooldown input
cd_entry = ttk.Entry(frm_left)
cd_entry.grid(column=1, row=2)
add_placeholder(cd_entry, "in seconds")

# text output
count_label = ttk.Label(frm_left, text="")
count_label.grid(column=0, row=11, columnspan=2)

# get the default image
photo = PhotoImage(file=resource_path("images/default image.png"))

# image of pokemon
image_label = ttk.Label(frm_right, image=photo)
image_label.grid(column=0, row=0)
image_label.image = photo


def update_size():
    root.update_idletasks()   # let Tkinter calculate widget sizes
    root.minsize(root.winfo_width(), root.winfo_height())
    root.maxsize(root.winfo_width(), root.winfo_height()) 

def fetch_valid_image(urls):
    """Tries a list of URLs and returns the first valid image URL."""
    for url in urls:
        try:
            response = requests.get(url, timeout=5)  # timeout to avoid hanging
            if response.status_code == 200:
                return response
        except requests.RequestException:
            continue  # skip if request failed
    return None


def add_shiny_icon(bytes):
    background = pimage.open(bytes).convert("RGBA")
    icon = pimage.open(resource_path("images/shiny_icon_red_512.png")).resize((50, 50), pimage.LANCZOS).convert("RGBA")

    # Versnelde pixelbewerking
    # Niets

    # Plak het icoon op de afbeelding
    position = (background.width - icon.width - 10, 10)
    background.paste(icon, position, icon)

    # Opslaan in geheugen
    output_bytes = BytesIO()
    background.save(output_bytes, format="PNG")
    output_bytes.seek(0)
    
    return output_bytes


def get_img(shiny, poke_id):
    # Bepaal de URL's
    base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other"
    official_art = f"{base_url}/official-artwork/{'shiny/' if shiny else ''}{poke_id}.png"
    fallback = [f"{base_url}/home/{'shiny/' if shiny else ''}{poke_id}.png"]

    # Controleer beschikbaarheid met één GET request
    img = fetch_valid_image([official_art] + fallback)
    if not img:
        return PhotoImage(file=resource_path("images/notfound.png"))
    
    img_bytes = BytesIO(img.content)

    if shiny:
        img_bytes = add_shiny_icon(img_bytes)

    reimage = pimage.open(img_bytes)
    resized = reimage.resize((600,600), pimage.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(resized)

    return photo


def encounter():
    mon = pkmn_entry.get()

    if mon:
        mon = mon.lower().replace(" ", "-")
        try:
            species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{mon}").json()
            dexnr =  species["id"]
            gennr = int(species['generation']['url'].split('/')[-2])

            pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon/{dexnr}").json()

        except:
            count_label.config(text=f"{mon.capitalize()} is not a valid Pokemon")
            return

    else:
        count_label.config(text=f"Please input a Pokemon name or dex number.")
        return

    if btn.old_mon == mon:
        btn.count += 1
    
    else:
        btn.count = 1
        btn.old_mon = mon

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
        odds = 8192 if gennr < 6 else 4096

    rand = random.randint(1,odds)
    shiny = rand == 1

    # print(f"odds: 1/{odds}, cooldown: {cooldown}, rand: {rand}, shiny: {shiny}")

    count_text = f"encounters done: {btn.count}"
    photo = get_img(shiny, dexnr)

    count_label.config(text=count_text)
    image_label.config(image=photo)
    image_label.image = photo  # <-- keep reference alive


btn = ttk.Button(frm_left, text="Encounter!", command=lambda: encounter())
btn.grid(column=0, row=10, columnspan=2, ipadx=30, ipady=10, pady=(10, 5))
btn.old_mon = ""
btn.count = 0

update_size()

root.mainloop()