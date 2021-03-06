import os
import shutil
import signal
import threading
import time

from colorama import *
from players import *
from pickle import *
import multiprocessing as mp
import sysv_ipc


class Board(mp.Process):
    def __init__(self, deck, cartesonboard, nbjoueurs):
        super().__init__()
        self.cartesonboard = cartesonboard
        self.deck = deck
        self.nbjoueurs = nbjoueurs
        self.printlock = mp.Lock()

    def afficheBoard(self, mqverifT):
        print("============================BOARD============================")
        nbdecartes = len(self.cartesonboard)
        fin = ""
        for card in self.cartesonboard:
            if card.couleur == "bleu":
                couleur = Fore.BLUE
            else:
                couleur = Fore.RED
            print(couleur + "╔═════════╗", end=fin)
        print("")
        for j in range(0, 7):
            for card in self.cartesonboard:
                if card.couleur == "bleu":
                    couleur = Fore.BLUE
                else:
                    couleur = Fore.RED
                if j == 3:
                    if card.numero >= 10:
                        print(couleur + "║   1 0   ║", end=fin)
                    else:
                        print(couleur + "║    " + str(card.numero) + "    ║", end=fin)
                else:
                    print(couleur + "║         ║", end=fin)
            print("")
        for card in self.cartesonboard:
            if card.couleur == "bleu":
                couleur = Fore.BLUE
            else:
                couleur = Fore.RED
            print(couleur + "╚═════════╝", end=fin, flush=True)
        print("" + Style.RESET_ALL)
        print("=============================================================")

    def verification(self, carterecue, mqverifT, mqhandsize, mqaffichage):
        valide = False
        for carte in self.cartesonboard:
            if (carte.couleur == carterecue.couleur) and (abs(carte.numero - carterecue.numero) == 1) and not valide:
                valide = True
            elif (carte.couleur != carterecue.couleur) and (carte.numero == carterecue.numero) and not valide:
                valide = True

        if valide:
            self.cartesonboard.append(carterecue)
            mqverifT[carterecue.numerojoueur - 1].send((str(True)).encode())
            nmbcarteshand, t = mqhandsize.receive()

            if int(nmbcarteshand.decode()) == 0:
                mqaffichage.send(str(1).encode(), type=4)
                with self.printlock:
                    stringfin = "Joueur " + str(carterecue.numerojoueur) + " gagne !"
                    print(stringfin.center(shutil.get_terminal_size()[0]))
                while not self.deck.empty():
                    self.deck.get()
        else:
            mqverifT[carterecue.numerojoueur - 1].send((str(False)).encode())

    def affichageforce(self, mqaffichage, mqverifT):
        while not self.deck.empty():
            _, _ = mqaffichage.receive(type=4)
            os.system('cls||clear')
            with self.printlock:
                self.afficheBoard(mqverifT)
            mqaffichage.send(str(1).encode(), type=1)
            time.sleep(0.01)
            mqaffichage.send(str(1).encode(), type=2)

    def run(self):
        mqverifT = []
        mqcards = sysv_ipc.MessageQueue(100)
        mqhandsize = sysv_ipc.MessageQueue(300)
        mqaffichage = sysv_ipc.MessageQueue(400)
        mains = []
        players = []
        keys = []

        for i in range(self.nbjoueurs):
            mains.append([])
            keys.append(i + 1)

            mqverif = sysv_ipc.MessageQueue(keys[i])
            mqverifT.append(mqverif)

            for j in range(1, 6):
                mains[i].append(self.deck.get())
                mains[i][j - 1].numerojoueur = i + 1

            players.append(Players(i + 1, self.deck, mains[i], self.printlock))

        for x in players:
            x.start()
        with self.printlock:
            threadaffichage = threading.Thread(target=self.affichageforce, args=(mqaffichage, mqverifT))
            threadaffichage.start()

        while True:
            mqaffichage.send(str(1).encode(), type=4)
            carterecue, t = mqcards.receive()
            self.verification(loads(carterecue), mqverifT, mqhandsize, mqaffichage)

