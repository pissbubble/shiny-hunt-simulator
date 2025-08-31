import requests
import random
from io import BytesIO
from PIL import Image as pimage
from tkinter import *
from tkinter import ttk
from tkinter import font

root = Tk()
root.title("Shiny Hunting Simulator")

big_font = font.Font(family="Arial", size=14)
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

# Entry box for user input
pkmn_entry = ttk.Entry(frm_left)
pkmn_entry.grid(column=1, row=0)

# Label for odds field
odds_label = ttk.Label(frm_left, text="odds?")
odds_label.grid(column=0, row=1)

# Entry box for user input
odds_entry = ttk.Entry(frm_left)
odds_entry.grid(column=1, row=1)

# Label for cooldown field
cd_label = ttk.Label(frm_left, text="cooldown? (seconds)")
cd_label.grid(column=0, row=2)

# Entry box for user input
cd_entry = ttk.Entry(frm_left)
cd_entry.grid(column=1, row=2)

# text output
count_label = ttk.Label(frm_left, text="")
count_label.grid(column=0, row=11, columnspan=2)

# image of pokemon
image_label = ttk.Label(frm_right)
image_label.grid(column=0, row=0)


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
    icon = pimage.open("images/shiny_icon_red_512.png").resize((50, 50), pimage.LANCZOS).convert("RGBA")

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
        return "https://i.imgur.com/CK0spW8.png"
    
    frm_rightbytes = BytesIO(img.content)

    if shiny:
        frm_rightbytes = add_shiny_icon(frm_rightbytes)

    return PhotoImage(data=frm_rightbytes.getvalue())


def encounter():
    mon = pkmn_entry.get()

    if mon:
        mon = mon.lower()
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

    count_text = f"encounters done: {btn.count}"
    photo = get_img(shiny, dexnr)

    count_label.config(text=count_text)
    image_label.config(image=photo)
    image_label.image = photo  # <-- keep reference alive

btn = ttk.Button(frm_left, text="Encounter!", command=lambda: encounter())
btn.grid(column=0, row=10, columnspan=2, ipadx=30, ipady=10, pady=(10, 5))
btn.old_mon = ""
btn.count = 0

root.mainloop()