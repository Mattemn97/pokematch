#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool avanzato per scegliere i migliori tipi Pokémon contro un avversario.

Caratteristiche:
- Query diretta alla PokeAPI
- Cache locale con versioning intelligente
- Ricerca per tipo o per nome Pokémon
- Filtri su generazione, stadio evolutivo ed esclusioni
- Barra di caricamento (tqdm)
- Stampa formattata a colori tramite colorama
"""

import os
import sys
import json
import requests
import urllib3
from tqdm import tqdm
from colorama import Fore, Style, init

# Inizializza colori
init(autoreset=True)

CACHE_FILE = "poke_cache.json"
CACHE_VERSION = "1.1"   # ⇦ cambia questo numero se modifichi struttura/filtri della cache
BASE_URL = "https://pokeapi.co/api/v2"


# ===================================================================
# FUNZIONI DI SUPPORTO
# ===================================================================

def load_cache():
    """Carica la cache locale se valida."""
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        if cache.get("version") != CACHE_VERSION:
            print(Fore.YELLOW + "[!] Cache obsoleta, rigenerazione...")
            return {}
        return cache
    except:
        return {}


def save_cache(cache):
    """Salva la cache locale includendo la versione."""
    cache["version"] = CACHE_VERSION
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def fetch_json(url):
    """Richiede JSON da un URL con gestione errori."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(Fore.RED + f"Errore rete: {e}")
        sys.exit(1)


# ===================================================================
# FUNZIONI API PRINCIPALI
# ===================================================================

def get_pokemon_data(name, cache):
    """Scarica dati completi su un Pokémon (tipi, evoluzioni, generazione)."""
    name = name.lower()

    if "pokemon" not in cache:
        cache["pokemon"] = {}

    if name in cache["pokemon"]:
        return cache["pokemon"][name]

    print(Fore.CYAN + f"Scarico dati Pokémon per {name}...")
    data = fetch_json(f"{BASE_URL}/pokemon/{name}")

    species_data = fetch_json(data["species"]["url"])
    evolution_chain = fetch_json(species_data["evolution_chain"]["url"])

    # Estrae generazione
    generation = species_data["generation"]["name"]

    # Determina lo stadio evolutivo
    evo = evolution_chain["chain"]
    evo_stage = 1
    while evo:
        if evo["species"]["name"] == name:
            break
        evo = evo["evolves_to"][0] if evo["evolves_to"] else None
        evo_stage += 1

    result = {
        "name": name,
        "types": [t["type"]["name"] for t in data["types"]],
        "generation": generation,
        "evolution_stage": evo_stage
    }

    cache["pokemon"][name] = result
    save_cache(cache)
    return result


def get_type_data(t, cache):
    """Scarica dati del singolo tipo (danni x2, 1/2, 0)."""
    t = t.lower()
    if "types" not in cache:
        cache["types"] = {}

    if t in cache["types"]:
        return cache["types"][t]

    print(Fore.CYAN + f"Scarico dati tipo {t}...")
    data = fetch_json(f"{BASE_URL}/type/{t}")

    dmg = data["damage_relations"]
    result = {
        "double": [x["name"] for x in dmg["double_damage_to"]],
        "half":   [x["name"] for x in dmg["half_damage_to"]],
        "zero":   [x["name"] for x in dmg["no_damage_to"]],
    }

    cache["types"][t] = result
    save_cache(cache)
    return result


# ===================================================================
# LOGICA DI CALCOLO
# ===================================================================

def calculate_best_types(target_types, cache):
    """Restituisce i tipi più forti contro i tipi avversari."""
    score = {}

    for enemy_type in target_types:
        tdata = get_type_data(enemy_type, cache)
        for t in tdata["double"]:
            score[t] = score.get(t, 0) + 2
        for t in tdata["half"]:
            score[t] = score.get(t, 0) - 1
        for t in tdata["zero"]:
            score[t] = score.get(t, 0) - 5

    sorted_types = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return sorted_types


# ===================================================================
# FILTRI SUI POKÉMON
# ===================================================================

def filter_pokemon_list(pokemon_list, gen=None, evo=None, exclude=None):
    """Applica filtri a una lista di Pokémon."""
    if exclude:
        exclude = [x.lower() for x in exclude]

    filtered = []
    for p in pokemon_list:
        if gen and p["generation"] != gen:
            continue
        if evo and p["evolution_stage"] != evo:
            continue
        if exclude and p["name"] in exclude:
            continue
        filtered.append(p)
    return filtered


def search_pokemon_by_types(best_types, cache):
    """Restituisce una lista di Pokémon che possiedono almeno uno dei tipi indicati."""
    result = []

    type_list = [x[0] for x in best_types]

    all_pokemon = fetch_json(f"{BASE_URL}/pokemon?limit=2000")["results"]

    print(Fore.CYAN + "Analisi estesa dei Pokémon...")
    for entry in tqdm(all_pokemon, ncols=80):
        name = entry["name"]
        pdata = get_pokemon_data(name, cache)

        # Se ha almeno uno dei tipi migliori
        if any(t in pdata["types"] for t in type_list):
            result.append(pdata)

    return result


# ===================================================================
# MENU INTERATTIVO
# ===================================================================

def choose_input_mode():
    print(Fore.MAGENTA + "\n=== Modalità input ===")
    print(Fore.WHITE + "1) Inserisco i tipi dell'avversario")
    print("2) Inserisco direttamente il nome del Pokémon")
    return input(Fore.YELLOW + "Scelta: ").strip()


def ask_filters():
    print(Fore.MAGENTA + "\n=== Filtri disponibili ===")
    gen = input(Fore.CYAN + "Generazione (es: generation-i) oppure vuoto: ").strip() or None
    evo = input(Fore.CYAN + "Stadio evolutivo (1-3) oppure vuoto: ").strip()

    evo = int(evo) if evo.isdigit() else None

    excl = input(Fore.CYAN + "Esclusioni (nomi separati da virgola) oppure vuoto: ").strip()
    excl = [x.strip() for x in excl.split(",")] if excl else None

    return gen, evo, excl


# ===================================================================
# MAIN
# ===================================================================

def main():
    print(Fore.GREEN + "\n=== Pokémon Counter Tool ===")

    cache = load_cache()

    mode = choose_input_mode()

    if mode == "1":
        types = input(Fore.YELLOW + "Inserisci 1 o 2 tipi separati da spazio: ").split()
        target_types = [x.lower() for x in types]

    elif mode == "2":
        name = input(Fore.YELLOW + "Inserisci il nome del Pokémon: ").strip()
        pdata = get_pokemon_data(name, cache)
        target_types = pdata["types"]
        print(Fore.CYAN + f"{name} → Tipi: {', '.join(target_types)}")

    else:
        print(Fore.RED + "Scelta non valida.")
        return

    print(Fore.BLUE + "\nCalcolo dei tipi efficaci...")
    best_types = calculate_best_types(target_types, cache)

    print(Fore.GREEN + "\n=== Tipi più efficaci ===")
    for t, s in best_types[:10]:
        color = Fore.GREEN if s > 0 else Fore.RED if s < 0 else Fore.WHITE
        print(f"{color}{t:<10}  →  score {s}")

    print(Fore.MAGENTA + "\nVuoi filtrare i Pokémon suggeriti?")
    gen, evo, excl = ask_filters()

    print(Fore.BLUE + "\nRicerca Pokémon più efficaci...")
    pokes = search_pokemon_by_types(best_types[:3], cache)
    pokes = filter_pokemon_list(pokes, gen, evo, excl)

    print(Fore.GREEN + f"\n=== Pokémon consigliati ({len(pokes)} trovati) ===")
    for p in pokes[:40]:
        print(Fore.WHITE + f"- {p['name']}  ({', '.join(p['types'])})  gen={p['generation']}  evo={p['evolution_stage']}")

    print(Fore.GREEN + "\nFatto!")


if __name__ == "__main__":
    main()
