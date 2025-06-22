#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch

# Initialisation
ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

capteur_gauche = ColorSensor(Port.S3)
capteur_droit = ColorSensor(Port.S2)

chrono = StopWatch()

# Seuils & vitesses
THRESHOLD_NOIR = 10  # Ajuste selon ta piste
VITESSE_INITIALE = 200
VITESSE_SUIVI = 500
VITESSE_TOURNE_FORT = 150

# États
depart = False
sur_rouge = False
passages_rouge = 0

# === Attente du départ (ligne rouge sur capteur gauche) ===
while not depart:
    r, g, b = capteur_gauche.rgb()
    ev3.screen.clear()
    ev3.screen.print("Attente ligne rouge...")
    ev3.screen.print("R:{} G:{} B:{}".format(r, g, b))

    if r > 2 * g and r > 2 * b:
        depart = True
        chrono.reset()
        ev3.screen.clear()
        ev3.screen.print("DEPART !")
        ev3.speaker.beep()

    wait(100)

# === Boucle principale ===
while True:
    # Détection rouge (arrivée)
    r, g, b = capteur_gauche.rgb()
    if r > 2 * g and r > 2 * b:
        if not sur_rouge:
            
            sur_rouge = True
            passages_rouge += 1
            ev3.speaker.beep()
            ev3.screen.clear()
            ev3.screen.print("Rouge #{}".format(passages_rouge))

        # Avance tout droit
        left_motor.run(VITESSE_SUIVI)
        right_motor.run(VITESSE_SUIVI)

        if passages_rouge >= 3:
            left_motor.stop()
            right_motor.stop()
            temps = chrono.time() / 1000
            ev3.screen.clear()
            ev3.screen.print("Terminé !")
            ev3.screen.print("Temps: {:.2f} s".format(temps))
            wait(5000)
            break
    else:
        sur_rouge = False

        # Mode reflect après départ
        gauche = capteur_gauche.reflection()
        droite = capteur_droit.reflection()

        # Suivi de ligne avec virages ajustés
        if gauche < THRESHOLD_NOIR and droite > THRESHOLD_NOIR:
            # Tourner fort à gauche
            left_motor.run(VITESSE_TOURNE_FORT)
            right_motor.run(VITESSE_SUIVI)
        elif droite < THRESHOLD_NOIR and gauche > THRESHOLD_NOIR:
            # Tourner fort à droite
            left_motor.run(VITESSE_SUIVI)
            right_motor.run(0)  # Stop moteur droit pour virage net
        elif droite < THRESHOLD_NOIR and gauche < THRESHOLD_NOIR:
            # Ligne au centre
            left_motor.run(VITESSE_SUIVI)
            right_motor.run(VITESSE_SUIVI)
        else:
            # Hors ligne : avance doucement
            left_motor.run(VITESSE_INITIALE)
            right_motor.run(VITESSE_INITIALE)

    wait(10)
