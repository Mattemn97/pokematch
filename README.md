# Pokémon Type Optimizer

Questo script permette di trovare **la combinazione migliore di tipi
Pokémon** per contrastare un avversario con uno o due tipi, tenendo
conto sia dell'efficacia **offensiva** sia della **resistenza
difensiva**.\
Infine suggerisce una lista di Pokémon reali che possiedono quei tipi.

## ✨ Funzionalità principali

-   Recupero automatico dei tipi dalla **PokeAPI**
-   Calcolo dei tipi più efficaci in **attacco**
-   Calcolo dei tipi più solidi in **difesa**
-   Combinazione dei due risultati per trovare i tipi più forti
    complessivi
-   Recupero dei Pokémon che hanno quei tipi
-   Input validato
-   Supporto a Pokémon con uno o due tipi

------------------------------------------------------------------------

## ▶️ Come usarlo

1.  Esegui lo script:

    ``` bash
    python3 script.py
    ```

2.  Alla richiesta, inserisci:

    -   Il primo tipo dell'avversario\
    -   Eventualmente il secondo (o lascia vuoto)

3.  Lo script mostrerà:

    -   I migliori tipi offensivi
    -   I migliori tipi difensivi
    -   La miglior combinazione totale
    -   I Pokémon consigliati

------------------------------------------------------------------------

## 🔧 Dipendenze

Lo script utilizza:

-   `requests`
-   `urllib3`

Installa tutto con:

``` bash
pip install requests urllib3
```

------------------------------------------------------------------------

## 🌐 API utilizzata

Lo script interroga la **PokeAPI**:\
https://pokeapi.co/

------------------------------------------------------------------------

## 📁 Struttura interna

Lo script è organizzato in sezioni:

1.  Caricamento tipi
2.  Analisi delle relazioni attacco/difesa
3.  Valutazione multiplier offensivi
4.  Punteggi difensivi
5.  Recupero Pokémon reali
6.  Combina attacco + difesa
7.  Input validato
8.  Output finale

------------------------------------------------------------------------

## 📜 Licenza

Questo progetto è rilasciato liberamente per uso personale e didattico.

Buon divertimento con le strategie Pokémon!
