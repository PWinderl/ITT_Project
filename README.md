# ITT_Project

Startup:
python3 -m pip install -U pygame --user

2 Spieler: Dirigent, Spieler

Auflösung: xdpyinfo | grep dimensions

## TodoList:

- Minigame
    - Templates definieren und in TemplateWidget darstellen
    - 2 Pointer implementieren
    - Gesten/Zeichenerkennung
    - 2 Bluetooth Inputs hinzufügen
- Eventsystem
- Sprites für Game
- 2 Wiimote handling
- Button Input
- Sounds einbinden (4 Töne)
- Menüscreen
- Bis auf game.py alles in einem großen Widget anzeigen
- Activity Recognizing
    - entweder FFT oder moving average (FFT wäre besser)
    - unbedingt mit SVM implementieren!
- Error im Minigame: manchmal 67 oder 72 Punkte statt 64 (resample)
- Error: y = point[1] * (size / box[1]) ZeroDivisionError: float division by zero bei scale_to_square


## Offene Themen:

- Welche activity? (Geige könnte Probleme verursachen)
- Sounds abspielen, wenn "Dirigent" Ton vorgibt?
