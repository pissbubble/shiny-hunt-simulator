import requests
import random
from io import BytesIO
from PIL import Image as pimage
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Shiny Hunting Simulator")


frm = ttk.Frame(root, padding=10)
frm.grid()


# Label for odds
pkmn_label = ttk.Label(frm, text="Pokemon?")
pkmn_label.grid(column=0, row=0)

# Entry box for user input
pkmn_entry = ttk.Entry(frm)
pkmn_entry.grid(column=1, row=0)

# Label for odds
odds_label = ttk.Label(frm, text="odds?")
odds_label.grid(column=0, row=1)

# Entry box for user input
odds_entry = ttk.Entry(frm)
odds_entry.grid(column=1, row=1)

# Label for cooldown
cd_label = ttk.Label(frm, text="cooldown? (seconds)")
cd_label.grid(column=0, row=2)

# Entry box for user input
cd_entry = ttk.Entry(frm)
cd_entry.grid(column=1, row=2)

#text output
result_label = ttk.Label(frm, text="")
result_label.grid(column=1, row=10)

image_label = ttk.Label(frm)
image_label.grid(column=0, row=8)


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
    
    img_bytes = BytesIO(img.content)

    if shiny:
        img_bytes = add_shiny_icon(img_bytes)

    return PhotoImage(data=img_bytes.getvalue())



def encounter():
    mon = pkmn_entry.get()

    if mon:
        mon = mon.lower()
        try:
            species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{mon}").json()
            dexnr =  species["id"]
            gennr = species['generation']['url'].split('/')[-2]

            pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon/{dexnr}").json()

        except:
            result_label.config(text=f"{mon.capitalize()} is not a valid Pokemon")
            return



    else:
        result_label.config(text=f"Please input a Pokemon name or dex number.")
        return

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

    rand = random.randint(1,odds)
    shiny = rand == 1

    photo = get_img(shiny, dexnr)

    result = "shiny" if shiny else "regular ass"

    result_label.config(text=result)
    image_label.config(image=photo)
    image_label.image = photo  # <-- keep reference alive

btn = ttk.Button(frm, text="Encounter!", command=lambda: encounter())
btn.grid(column=0, row=10)

root.mainloop()