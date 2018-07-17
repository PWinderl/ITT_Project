# ITT_Project

Startup:
python3 -m pip install -U pygame --user

2 Spieler: Dirigent, Spieler

Auflösung: xdpyinfo | grep dimensions

## TodoList:

- Minigame
    - ~~Templates definieren und in TemplateWidget darstellen~~
    - ~~2 Pointer implementieren (Rechtecke, die den jeweiligen Cursor repräsentieren)~~
    - Gesten/Zeichenerkennung muss funktionieren
    - ~~2 Bluetooth Inputs hinzufügen~~
- ~~2 Wiimote handling~~
- ~~Button Input~~
- ~~Menüscreen~~
- ~~Bis auf game.py alles in einem großen Widget anzeigen~~
- ~~Activity Recognizing~~
- Game
    - Sounds einbinden (4 Töne) !
    - Einbinden der Activity Recognition
    - Minigame Timer !
    - Randwidget mit Punkteanzahl !
    - Minimizing !
- Setup
    - ~~Bluetooth connection abfragen / Events
    - ~~Bevor Verbindung steht, setup screen anzeigen -> evtl anderer Thread für Verbindungsaufbau~~
    - ~~Hintergrund~~
    - Text styling
- ~~Wechsel von Game zu Minigame und wieder zurück !~~
- GUI
    - Sprites
        - ~~"Target" also Kreise, die das Ziel darstellen~~
        - ~~"Cube" Noten, die durch die Lines fahren~~
        - ~~"Line" abgrenzende Linie~~
    - Hintergrund
        - ~~für main widget~~
        - für Widgets
        - für pygame (wenn möglich / nötig)
    - Buttons


## Errors

- Error im Minigame: manchmal 67 oder 72 Punkte statt 64 (resample)
- Error: y = point[1] * (size / box[1]) ZeroDivisionError: float division by zero bei scale_to_square
- Error in Game:
    - QObject::~QObject: Timers cannot be stopped from another thread
    - Segmentation fault


## Offene Themen:

- Welche activity? (Geige könnte Probleme verursachen)
- Sounds abspielen, wenn "Dirigent" Ton vorgibt?

## Sounds:

- C F G A
- C D F G
- C ES F G
- C ES G A

oder chords:
- C E G
- G B D
- A C E
- F A C
