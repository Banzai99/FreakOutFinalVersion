import os
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
            print(couleur + "╚════════╝", end=fin, flush=True)
        print("" + Style.RESET_ALL)
        print("=============================================================")

    def verification(self, carterecue, mqverifT, mqhandsize, mqaffichage):
        valide = False
        for carte in self.cartesonboard:
            if (carte.couleur == carterecue.couleur) and (abs(carte.numero - carterecue.numero) == 1) and not valide:
                # print(str(mp.current_process()) + " | Carte valide")
                valide = True
            elif (carte.couleur != carterecue.couleur) and (carte.numero == carterecue.numero) and not valide:
                # print(str(mp.current_process()) + " | Carte valide")
                valide = True

        if valide:
            self.cartesonboard.append(carterecue)
            # print(str(mp.current_process()) + " | Move valide, on process mais pas recu")
            mqverifT[carterecue.numerojoueur - 1].send((str(True)).encode())
            # nmbcarteshand, t = mqverifT[carterecue.numerojoueur].receive()
            nmbcarteshand, t = mqhandsize.receive()
            # print(str(mp.current_process()) + " | Move valide, on process")

            if int(nmbcarteshand.decode()) == 0:
                with self.printlock:
                    self.afficheBoard(mqverifT)
                mqaffichage.send(str(1).encode(), type=1)
                time.sleep(0.01)
                mqaffichage.send(str(1).encode(), type=2)
                print("Joueur " + str(carterecue.numerojoueur) + " gagne !")
                while not self.deck.empty():
                    self.deck.get()
        else:
            # print(str(mp.current_process()) + " | Tu pioches")
            mqverifT[carterecue.numerojoueur - 1].send((str(False)).encode())

        # print(str(mp.current_process()) + " | allo")

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
            # print(mqverifT[i])

            for j in range(1, 6):
                mains[i].append(self.deck.get())
                mains[i][j - 1].numerojoueur = i + 1

            # print("joueur crée")
            players.append(Players(i + 1, self.deck, mains[i], self.printlock))
            # print(players[i])

        for x in players:
            # print("jouons !")
            x.start()
        # affichage = threading.Thread(target=self.afficheBoard, args=(mqverifT,))
        # affichage.start()

        while True:
            os.system('cls||clear')
            with self.printlock:
                self.afficheBoard(mqverifT)
            mqaffichage.send(str(1).encode(), type=1)
            time.sleep(0.01)
            mqaffichage.send(str(1).encode(), type=2)
            # print(str(mp.current_process()) + " | and now we wait for a card")
            carterecue, t = mqcards.receive()
            # print(str(mp.current_process()) + " | Carte recue !")
            self.verification(loads(carterecue), mqverifT, mqhandsize, mqaffichage)
