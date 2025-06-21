#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait, StopWatch

# Initialisation
ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
capteur_gauche = ColorSensor(Port.S3)
capteur_droit = ColorSensor(Port.S2)
capteur_ultrason = UltrasonicSensor(Port.S4)

chrono = StopWatch()

# Seuils & vitesses
THRESHOLD_NOIR = 10
VITESSE_INITIALE = 200
VITESSE_SUIVI = 300
VITESSE_TOURNE_FORT = 150
vitesse = 160
vitesse2 = 190

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
    # === Détection d'obstacle avec l'ultrason ===
    distance = capteur_ultrason.distance()
    if distance < 100:  # distance en mm
        ev3.screen.clear()
        ev3.screen.print("Obstacle detecté !")

        # Stoppe le robot avant la manœuvre
        left_motor.stop()
        right_motor.stop()
        wait(500)

        # Tourner à droite
        left_motor.run_angle(vitesse, vitesse, Stop.HOLD, False)
        right_motor.run_angle(vitesse, -vitesse, Stop.HOLD, True)
        wait(100)

        # Avancer 20 cm
        left_motor.run(500)  # approx 20 cm
        right_motor.run(500)
        wait(1000)

        # Tourner à gauche
        left_motor.run_angle(vitesse2, -vitesse2, Stop.HOLD, False)
        right_motor.run_angle(vitesse2, vitesse2, Stop.HOLD, True)
        wait(100)

        # Avancer 20 cm
        left_motor.run(900)  # approx 20 cm
        right_motor.run(900)
        wait(1500)

        # Tourner à gauche
        left_motor.run_angle(170, -170, Stop.HOLD, False)
        right_motor.run_angle(170, 170, Stop.HOLD, True)
        wait(2000)

        # Avancer 20 cm
        left_motor.run(600)  # approx 20 cm
        right_motor.run(600)
        wait(1000)

        # Tourner à droite
        left_motor.run_angle(180, 180, Stop.HOLD, False)
        right_motor.run_angle(180, -180, Stop.HOLD, True)
        
        continue  # Reprendre la boucle (sans suivre la ligne sur ce cycle)

    # === Détection rouge (arrivée) ===
    r, g, b = capteur_gauche.rgb()
    if r > 2 * g and r > 2 * b:
        if not sur_rouge:
            sur_rouge = True
            passages_rouge += 1
            ev3.speaker.beep()
            ev3.screen.clear()
            ev3.screen.print("Rouge #{}".format(passages_rouge))

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

        # Suivi de ligne
        gauche = capteur_gauche.reflection()
        droite = capteur_droit.reflection()

        if gauche < THRESHOLD_NOIR and droite > THRESHOLD_NOIR:
            left_motor.run(0)
            right_motor.run(VITESSE_SUIVI)
        elif droite < THRESHOLD_NOIR and gauche > THRESHOLD_NOIR:
            left_motor.run(VITESSE_SUIVI)
            right_motor.run(0)
        elif droite < THRESHOLD_NOIR and gauche < THRESHOLD_NOIR:
            left_motor.run(VITESSE_SUIVI)
            right_motor.run(VITESSE_SUIVI)
        else:
            left_motor.run(VITESSE_INITIALE)
            right_motor.run(VITESSE_INITIALE)

    wait(10)
