#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script per trovare la COMBINAZIONE MIGLIORE DI TIPI POKÉMON
contro un avversario dato uno o due tipi, basata sia su:

- efficacia offensiva
- resistenza difensiva

E infine suggerisce Pokémon reali che possiedono quei tipi.

✔ Aggiornamento automatico tramite PokeAPI
✔ Mostra tipi disponibili
✔ Input validato
✔ Calcolo del miglior tipo offensivo
✔ Calcolo del miglior tipo difensivo
✔ Combina i risultati per trovare la miglior coppia di tipi
✔ Ricerca Pokémon che hanno quel/i tipo/i
"""

import requests
import urllib3
from itertools import combinations

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

POKEAPI_BASE = "https://pokeapi.co/api/v2/"


# ------------------------------------------------------------
# 1️⃣ Recupero tipi
# ------------------------------------------------------------
def fetch_types():
    url = f"{POKEAPI_BASE}type/"
    res = requests.get(url, verify=False).json()
    types = [t["name"] for t in res["results"] if t["name"] not in ["shadow", "unknown"]]
    return types


# ------------------------------------------------------------
# 2️⃣ Recupero relazioni tipo/attacco/difesa
# ------------------------------------------------------------
def fetch_type_relations():
    types = fetch_types()
    relations = {}

    for t in types:
        url = f"{POKEAPI_BASE}type/{t}/"
        r = requests.get(url, verify=False).json()
        relations[t] = {
            "attack": {
                "double": [x["name"] for x in r["damage_relations"]["double_damage_to"]],
                "half":   [x["name"] for x in r["damage_relations"]["half_damage_to"]],
                "zero":   [x["name"] for x in r["damage_relations"]["no_damage_to"]],
            },
            "defense": {
                "double": [x["name"] for x in r["damage_relations"]["double_damage_from"]],
                "half":   [x["name"] for x in r["damage_relations"]["half_damage_from"]],
                "zero":   [x["name"] for x in r["damage_relations"]["no_damage_from"]],
            }
        }
    return relations


# ------------------------------------------------------------
# 3️⃣ Calcolo moltiplicatore d'attacco
# ------------------------------------------------------------
def get_multiplier(attacker, enemy_types, relations):
    mult = 1
    for et in enemy_types:
        if et in relations[attacker]["attack"]["double"]:
            mult *= 2
        if et in relations[attacker]["attack"]["half"]:
            mult *= 0.5
        if et in relations[attacker]["attack"]["zero"]:
            mult *= 0
    return mult


# ------------------------------------------------------------
# 4️⃣ Calcolo vulnerabilità difensiva
# ------------------------------------------------------------
def get_defense_score(my_type, enemy_types, relations):
    score = 0
    for et in enemy_types:
        # che danno fa l'avversario A me
        if my_type in relations[et]["attack"]["double"]:
            score -= 2
        if my_type in relations[et]["attack"]["half"]:
            score += 1
        if my_type in relations[et]["attack"]["zero"]:
            score += 3
    return score


# ------------------------------------------------------------
# 5️⃣ Recupero tutti i Pokémon con tipi
# ------------------------------------------------------------
def fetch_all_pokemon():
    limit = 10000
    res = requests.get(f"{POKEAPI_BASE}pokemon?limit={limit}", verify=False).json()

    pokemon_list = []
    for p in res["results"]:
        data = requests.get(p["url"], verify=False).json()
        types = [t["type"]["name"] for t in data["types"]]
        pokemon_list.append({"name": data["name"], "types": types})
    return pokemon_list


# ------------------------------------------------------------
# 6️⃣ Migliori tipi offensivi
# ------------------------------------------------------------
def best_offensive(enemy_types, relations):
    scores = []
    for t in relations.keys():
        mult = get_multiplier(t, enemy_types, relations)
        scores.append((t, mult))

    max_mult = max(s for _, s in scores)
    return [t for t, m in scores if m == max_mult]


# ------------------------------------------------------------
# 7️⃣ Migliori tipi difensivi
# ------------------------------------------------------------
def best_defensive(enemy_types, relations):
    scores = []
    for t in relations.keys():
        s = get_defense_score(t, enemy_types, relations)
        scores.append((t, s))

    max_score = max(s for _, s in scores)
    return [t for t, s in scores if s == max_score]


# ------------------------------------------------------------
# 8️⃣ Combina attacco + difesa
# ------------------------------------------------------------
def combine_types(best_att, best_def):
    inter = list(set(best_att).intersection(best_def))
    if inter:
        return inter  # Jackpot: ottimi attacco + ottima difesa
    return list(set(best_att + best_def))


# ------------------------------------------------------------
# 9️⃣ Pokémon che hanno questi tipi
# ------------------------------------------------------------
def pokemon_with_types(types, pokemon_list):
    result = []
    for p in pokemon_list:
        if any(t in p["types"] for t in types):
            result.append(p)
    return result


# ------------------------------------------------------------
# 🔟 Input validato
# ------------------------------------------------------------
def get_valid_enemy_types(valid_types):
    print("\nTIPI DISPONIBILI:")
    print(", ".join(t.upper() for t in sorted(valid_types)))
    print()

    while True:
        t1 = input("Tipo avversario 1: ").strip().lower()
        if t1 not in valid_types:
            print(f"❌ '{t1}' non è un tipo valido.\n")
            continue

        t2 = input("Tipo avversario 2 (invio se nessuno): ").strip().lower()

        if t2 == "":
            return [t1]

        if t2 not in valid_types:
            print(f"❌ '{t2}' non è un tipo valido.\n")
            continue

        return [t1, t2]


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("Caricamento tipi Pokémon…")
    relations = fetch_type_relations()
    valid_types = list(relations.keys())

    print("Caricamento lista Pokémon…")
    pokemon_list = fetch_all_pokemon()

    enemy_types = get_valid_enemy_types(valid_types)
    print(f"\nTipi avversario: {enemy_types}")

    # Analisi
    best_att = best_offensive(enemy_types, relations)
    best_def = best_defensive(enemy_types, relations)
    combined = combine_types(best_att, best_def)

    print("\n🔥 MIGLIORI TIPI OFFENSIVI:", ", ".join(t.upper() for t in best_att))
    print("🛡 MIGLIORI TIPI DIFENSIVI:", ", ".join(t.upper() for t in best_def))
    print("\n💎 MIGLIOR COMBINAZIONE COMPLESSIVA:", ", ".join(t.upper() for t in combined))

    print("\nPokémon consigliati:")
    found = pokemon_with_types(combined, pokemon_list)
    for p in found[:50]:
        print(f"- {p['name'].capitalize()} ({', '.join(p['types']).upper()})")


if __name__ == "__main__":
    main()
