import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import requests
from PIL import Image, ImageTk
import io
import time
from functools import partial

# List of the original 151 Pokémon
POKEMON_LIST = ['bulbasaur', 'ivysaur', 'venusaur', 'charmander', 'charmeleon', 'charizard', 
    'squirtle', 'wartortle', 'blastoise','caterpie', 'metapod', 'butterfree', 'weedle', 'kakuna', 'beedrill', 
    'pidgey', 'pidgeotto', 'pidgeot', 'rattata', 'raticate', 'spearow','fearow', 'ekans', 'arbok', 'pikachu', 'raichu', 
    'sandshrew', 'sandslash','nidoran-f', 'nidorina', 'nidoqueen', 'nidoran-m', 'nidorino', 'nidoking', 
    'clefairy', 'clefable','vulpix', 'ninetales','jigglypuff', 'wigglytuff', 'zubat', 'golbat', 
    'oddish', 'gloom', 'vileplume', 'paras', 'parasect', 'venonat', 'venomoth', 'diglett', 'dugtrio', 
    'meowth', 'persian', 'psyduck', 'golduck', 'mankey', 'primeape', 'growlithe', 'arcanine', 
    'poliwag', 'poliwhirl', 'poliwrath', 'abra', 'kadabra', 'alakazam', 
    'machop', 'machoke', 'machamp', 'bellsprout', 'weepinbell', 'victreebel', 'tentacool', 'tentacruel', 
    'geodude', 'graveler', 'golem', 'ponyta', 'rapidash', 'slowpoke', 'slowbro', 'magnemite', 'magneton', 'farfetchd', 'doduo', 'dodrio',
    'seel', 'dewgong','grimer', 'muk', 'shellder', 'cloyster', 'gastly', 'haunter', 'gengar', 'onix', 
    'drowzee', 'hypno', 'krabby', 'kingler', 'voltorb', 'electrode', 'exeggcute', 'exeggutor', 
    'cubone', 'marowak', 'hitmonlee', 'hitmonchan', 'lickitung', 'koffing', 'weezing', 
    'rhyhorn', 'rhydon', 'chansey', 'tangela', 'kangaskhan', 'horsea', 'seadra', 'goldeen', 'seaking', 
    'staryu', 'starmie', 'mr-mime', 'scyther', 'jynx', 'electabuzz', 'magmar', 'pinsir', 
    'tauros', 'magikarp', 'gyarados', 'lapras', 'ditto', 'eevee', 'vaporeon', 'jolteon', 'flareon', 'porygon', 'omanyte', 'omastar', 
    'kabuto', 'kabutops', 'aerodactyl', 'snorlax', 'articuno', 'zapdos', 'moltres', 'dratini', 'dragonair', 'dragonite', 'mewtwo', 'mew']

# Global variables
current_pokemon = None
is_shiny = False
encounter_count = 0
total_encounters_before_shiny = 0
pokedex = []
pokedex_images = []
pokedex_encounters = []
pokedex_value = []
pokedex_cash = 0
berry_count = 0
master_ball_count = 0
is_encounter_active = False
berry_used = False
shiny_caught = 0
regular_caught = 0
unique_pokemon_caught = set()

def get_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            time.sleep(1)  # Add a 1-second delay to avoid rate limiting
            return response.json()
        else:
            print(f"Failed to fetch data for {pokemon_name}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching data for {pokemon_name}: {e}")
        return None

def get_pokemon_image(pokemon_data, shiny=False):
    try:
        img_url = pokemon_data['sprites']['front_shiny'] if shiny else pokemon_data['sprites']['front_default']
        img_response = requests.get(img_url)
        img_data = img_response.content
        image = Image.open(io.BytesIO(img_data))
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None

def start_encounter():
    global current_pokemon, is_shiny, encounter_count, total_encounters_before_shiny, is_encounter_active, berry_used
    if is_encounter_active:
        messagebox.showinfo("Error", "You must catch or run away from the current Pokémon before starting a new encounter.")
        return

    selected_pokemon = pokemon_var.get()
    current_pokemon = get_pokemon_data(selected_pokemon)

    if current_pokemon:
        encounter_count += 1
        total_encounters_before_shiny += 1
        encounter_counter_label.config(text=f"Encounters Before Shiny: {total_encounters_before_shiny}")

        is_shiny = random.randint(1, 4096) == 1  # 1 in 4096 chance for shiny
        pokemon_name = current_pokemon['name'].capitalize()
        
        if is_shiny:
            encounter_label.config(text=f"You encountered a shiny {pokemon_name}!")
            total_encounters_before_shiny = 0
        else:
            encounter_label.config(text=f"You encountered a normal {pokemon_name}!")

        pokemon_image = get_pokemon_image(current_pokemon, shiny=is_shiny)
        if pokemon_image:
            pokemon_label.config(image=pokemon_image)
            pokemon_label.image = pokemon_image
        else:
            pokemon_label.config(text="Image not available")

        catch_button.pack(pady=5)
        run_button.pack(pady=5)
        
        is_encounter_active = True
        berry_used = False
    else:
        encounter_label.config(text="Error: Could not fetch Pokémon data")

def attempt_catch(use_master_ball=False):
    global pokedex, pokedex_images, pokedex_encounters, pokedex_value, is_encounter_active, shiny_caught, regular_caught, unique_pokemon_caught
    if not is_encounter_active:
        messagebox.showinfo("Error", "No active encounter!")
        return

    catch_success = False
    
    if use_master_ball:
        catch_success = True
    else:
        catch_chance = 0.6 if not is_shiny else 0.25
        catch_chance += 0.15 * berry_used
        catch_chance = min(catch_chance, 1.0)
        catch_success = random.random() < catch_chance

    if catch_success:
        caught_name = current_pokemon['name'].capitalize()
        caught_image = get_pokemon_image(current_pokemon, shiny=is_shiny)
        pokedex.append(caught_name)
        pokedex_images.append(caught_image)
        pokedex_encounters.append(total_encounters_before_shiny)

        if is_shiny:
            messagebox.showinfo("Congratulations!", f"You caught a shiny {caught_name}!")
            value = 200000
            shiny_caught += 1
        else:
            messagebox.showinfo("Congratulations!", f"You caught a {caught_name}!")
            value = 200
            regular_caught += 1
        
        unique_pokemon_caught.add(caught_name.lower())
        pokedex_value.append(value)
        update_counter_display()
    else:
        messagebox.showinfo("Oops!", f"{current_pokemon['name'].capitalize()} escaped!")

    reset_buttons()

def run_away():
    global is_encounter_active
    if is_encounter_active:
        messagebox.showinfo("Run Away!", f"You ran away from {current_pokemon['name'].capitalize()}.")
        reset_buttons()
    else:
        messagebox.showinfo("Error", "No active encounter to run from!")

def reset_buttons():
    global is_encounter_active, berry_used
    catch_button.pack_forget()
    run_button.pack_forget()
    encounter_label.config(text="Press 'Start Encounter' to begin!")
    is_encounter_active = False
    berry_used = False

def show_pokedex():
    pokedex_window = tk.Toplevel(root)
    pokedex_window.title("Pokédex")
    pokedex_window.geometry("400x500")

    def refresh_pokedex():
        for widget in inner_frame.winfo_children():
            widget.destroy()

        pokedex_label = tk.Label(inner_frame, text="Pokédex", font=("Helvetica", 16, "bold"))
        pokedex_label.pack(pady=10)

        if pokedex:
            for i in range(len(pokedex)):
                pokemon_entry = tk.Frame(inner_frame)
                pokemon_entry.pack(pady=5, padx=10, fill=tk.X)

                pokemon_name_label = tk.Label(pokemon_entry, text=pokedex[i], font=("Helvetica", 14))
                pokemon_name_label.pack(side='left')

                if pokedex_images[i]:
                    pokemon_image_label = tk.Label(pokemon_entry, image=pokedex_images[i])
                    pokemon_image_label.image = pokedex_images[i]
                    pokemon_image_label.pack(side='right')

                encounters_label = tk.Label(pokemon_entry, text=f"Encounters: {pokedex_encounters[i]}", font=("Helvetica", 12))
                encounters_label.pack(side='bottom')

                sell_button = tk.Button(pokemon_entry, text="Sell", command=partial(sell_pokemon, i, refresh_pokedex))
                sell_button.pack(side='bottom')
        else:
            empty_label = tk.Label(inner_frame, text="No Pokémon caught yet!", font=("Helvetica", 14))
            empty_label.pack()

    canvas = tk.Canvas(pokedex_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(pokedex_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    refresh_pokedex()

def sell_pokemon(index, refresh_callback):
    global pokedex_cash, shiny_caught, regular_caught, unique_pokemon_caught
    if 0 <= index < len(pokedex):
        pokemon_value = pokedex_value[index]
        pokedex_cash += pokemon_value
        sold_pokemon = pokedex.pop(index)
        sold_image = pokedex_images.pop(index)
        pokedex_encounters.pop(index)
        sold_value = pokedex_value.pop(index)

        if sold_value == 200000:
            shiny_caught -= 1
        else:
            regular_caught -= 1

        if sold_pokemon.lower() not in [p.lower() for p in pokedex]:
            unique_pokemon_caught.remove(sold_pokemon.lower())

        messagebox.showinfo("Sold!", f"{sold_pokemon} sold for {pokemon_value} PokeCash!")
        update_cash_display()
        update_counter_display()
        refresh_callback()
    else:
        messagebox.showinfo("Error", "Invalid Pokémon selection!")

def update_cash_display():
    cash_label.config(text=f"PokeCash: {pokedex_cash}")

def update_counter_display():
    total_unique = len(unique_pokemon_caught)
    counter_label.config(text=f"Pokémon Caught: {total_unique}/151 | Shiny: {shiny_caught} | Regular: {regular_caught}")

def open_store():
    store_window = tk.Toplevel(root)
    store_window.title("Pokémon Store")

    store_cash_label = tk.Label(store_window, text=f"PokeCash: {pokedex_cash}", font=("Helvetica", 16))
    store_cash_label.pack(pady=10)

    buy_berries_button = tk.Button(store_window, text="Buy Berries (1000 PokeCash)", command=buy_berries)
    buy_berries_button.pack(pady=10)

    buy_master_ball_button = tk.Button(store_window, text="Buy Master Ball (100000 PokeCash)", command=buy_master_ball)
    buy_master_ball_button.pack(pady=10)

def buy_berries():
    global berry_count, pokedex_cash
    if pokedex_cash >= 1000:
        berry_count += 1
        pokedex_cash -= 1000
        messagebox.showinfo("Bought!", "You bought a berry!")
        update_cash_display()
    else:
        messagebox.showinfo("Error", "Not enough PokeCash to buy a berry!")

def buy_master_ball():
    global master_ball_count, pokedex_cash
    if pokedex_cash >= 100000:
        master_ball_count += 1
        pokedex_cash -= 100000
        messagebox.showinfo("Bought!", "You bought a Master Ball!")
        update_cash_display()
    else:
        messagebox.showinfo("Error", "Not enough PokeCash to buy a Master Ball!")

def open_item_bag():
    item_bag_window = tk.Toplevel(root)
    item_bag_window.title("Item Bag")

    item_label = tk.Label(item_bag_window, text=f"Berries: {berry_count}, Master Balls: {master_ball_count}", font=("Helvetica", 16))
    item_label.pack(pady=10)

    use_berry_button = tk.Button(item_bag_window, text="Use Berry", command=use_berry)
    use_berry_button.pack(pady=10)

    use_master_ball_button = tk.Button(item_bag_window, text="Use Master Ball", command=use_master_ball)
    use_master_ball_button.pack(pady=10)

def use_berry():
    global berry_count, berry_used
    if berry_count > 0 and not berry_used and is_encounter_active:
        berry_count -= 1
        berry_used = True
        messagebox.showinfo("Used Berry", "You used a berry to increase your catch odds!")
    elif not is_encounter_active:
        messagebox.showinfo("Error", "No active encounter to use a berry on!")
    elif berry_used:
        messagebox.showinfo("Error", "You can only use one berry per encounter!")
    else:
        messagebox.showinfo("Error", "No berries left!")

def use_master_ball():
    global master_ball_count
    if master_ball_count > 0 and is_encounter_active:
        master_ball_count -= 1
        attempt_catch(use_master_ball=True)
    elif not is_encounter_active:
        messagebox.showinfo("Error", "No active encounter to use a Master Ball on!")
    else:
        messagebox.showinfo("Error", "No Master Balls left!")

# Initialize the Tkinter window
root = tk.Tk()
root.title("Pokémon Shiny Hunt Simulator")

# Dropdown for selecting Pokémon
pokemon_var = tk.StringVar(value=POKEMON_LIST[0])
pokemon_dropdown = tk.OptionMenu(root, pokemon_var, *POKEMON_LIST)
pokemon_dropdown.pack(pady=10)

# Labels for encounter display
encounter_counter_label = tk.Label(root, text="Encounters Before Shiny: 0", font=("Helvetica", 14))
encounter_counter_label.pack(pady=10)

encounter_label = tk.Label(root, text="Press 'Start Encounter' to begin!", font=("Helvetica", 14))
encounter_label.pack(pady=10)

# Image label for Pokémon
pokemon_label = tk.Label(root)
pokemon_label.pack(pady=10)

# Buttons for starting an encounter, catching, and running away
start_button = tk.Button(root, text="Start Encounter", command=start_encounter)
start_button.pack(pady=5)

catch_button = tk.Button(root, text="Catch Pokémon", command=lambda: attempt_catch(use_master_ball=False))
run_button = tk.Button(root, text="Run Away", command=run_away)

# Button to show the Pokédex
pokedex_button = tk.Button(root, text="Show Pokédex", command=show_pokedex)
pokedex_button.pack(pady=5)

# Button to open the store
store_button = tk.Button(root, text="Open Store", command=open_store)
store_button.pack(pady=5)

# Button to open the item bag
item_bag_button = tk.Button(root, text="Open Item Bag", command=open_item_bag)
item_bag_button.pack(pady=5)

# Label to display current PokeCash
cash_label = tk.Label(root, text=f"PokeCash: {pokedex_cash}", font=("Helvetica", 14))
cash_label.pack(pady=5)

# Counter label for Pokémon caught
counter_label = tk.Label(root, text="Pokémon Caught: 0/151 | Shiny: 0 | Regular: 0", font=("Helvetica", 12))
counter_label.pack(side=tk.BOTTOM, pady=10)

# Update the counter display initially
update_counter_display()

# Start the Tkinter main loop
root.mainloop()