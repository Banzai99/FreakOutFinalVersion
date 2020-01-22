import random
import shutil
import time
from threading import Timer
import multitimer
import sysv_ipc
from board import *
from cards import *
from KBHit import *
import multiprocessing as mp


def printdeck(deck):
    for obj in deck:
        print(obj)


def commencementdujeu(nbjoueurs):
    decklist = []
    cartesonboard = []
    keys = []
    mqverifT = []
    lockverif = mp.Lock()
    deck = mp.Queue(20)
    # On crée un deck mélangé
    for i in range(10):
        decklist.append(Cards(i + 1, "bleu"))
        decklist.append(Cards(i + 1, "rouge"))
    random.shuffle(decklist)
    # On le convertit ensuite en queue afin de pouvoir le partager à tous les process
    for card in decklist:
        deck.put(card)
    cartesonboard.append(deck.get())

    mqtouchejouee1 = sysv_ipc.MessageQueue
    mqtouchejouee2 = sysv_ipc.MessageQueue
    mqcards = sysv_ipc.MessageQueue
    mqhandsize = sysv_ipc.MessageQueue
    mqaffichage = sysv_ipc.MessageQueue

    try:
        mqtouchejouee1 = sysv_ipc.MessageQueue(201, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        sysv_ipc.MessageQueue(201).remove()
        mqtouchejouee1 = sysv_ipc.MessageQueue(201, sysv_ipc.IPC_CREX)
    try:
        mqtouchejouee2 = sysv_ipc.MessageQueue(202, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        sysv_ipc.MessageQueue(202).remove()
        mqtouchejouee2 = sysv_ipc.MessageQueue(202, sysv_ipc.IPC_CREX)
    try:
        mqcards = sysv_ipc.MessageQueue(100, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        sysv_ipc.MessageQueue(100).remove()
        mqcards = sysv_ipc.MessageQueue(100, sysv_ipc.IPC_CREX)
    try:
        mqhandsize = sysv_ipc.MessageQueue(300, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        sysv_ipc.MessageQueue(300).remove()
        mqhandsize = sysv_ipc.MessageQueue(300, sysv_ipc.IPC_CREX)
    try:
        mqaffichage = sysv_ipc.MessageQueue(400, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        sysv_ipc.MessageQueue(400).remove()
        mqaffichage = sysv_ipc.MessageQueue(400, sysv_ipc.IPC_CREX)

    # Initialisation des différents process (board et les joueurs)
    board = Board(deck, cartesonboard, nbjoueurs)

    for i in range(nbjoueurs):
        keys.append(i + 1)
        try:
            mqverif = sysv_ipc.MessageQueue(keys[i], sysv_ipc.IPC_CREX)
            mqverifT.append(mqverif)
        except sysv_ipc.ExistentialError:
            sysv_ipc.MessageQueue(keys[i]).remove()

    # Démarrage des process
    board.start()

    # print('Lancement de la lecture de clavier non bloquante')
    touchesjoueurs = [['a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o'], ['1', '2', '3', '4', '5', '6', '7', '8', '9']]
    try:
        kb = KBHit()
        while not deck.empty():
            if kb.kbhit():
                c = kb.getch()
                if c in touchesjoueurs[0]:
                    mqtouchejouee1.send(str((touchesjoueurs[0].index(c) + 1)).encode())
                elif c in touchesjoueurs[1]:
                    mqtouchejouee2.send(c.encode())
                else:
                    print("Veuillez entrer une touche valide")
        mqcards.remove()
        mqtouchejouee1.remove()
        mqtouchejouee2.remove()
        mqhandsize.remove()
        mqaffichage.remove()
        for x in mqverifT:
            x.remove()
        os.killpg(os.getpgid(board.pid), signal.SIGTERM)

    except KeyboardInterrupt:
        print("Le grand nettoyage")
        mqcards.remove()
        mqtouchejouee1.remove()
        mqtouchejouee2.remove()
        mqhandsize.remove()
        mqaffichage.remove()
        for x in mqverifT:
            x.remove()
        os.killpg(os.getpgid(board.pid), signal.SIGTERM)


if __name__ == "__main__":
    os.system('clear')
    size = shutil.get_terminal_size()
    print("FreakOut, The Game".center(size[0]))
    print("Player 1 plays with \"AZERTYUIOP\" | Player 2 plays with \"123456789\"".center(size[0]))
    print("La position de la carte dans la main s'affiche en bas de la carte afin de la retrouver plus facilement".center(size[0]))
    time.sleep(8)
    commencementdujeu(2)

