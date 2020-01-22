import multiprocessing as mp
import threading
from threading import Timer
import multitimer
import sysv_ipc
import os
from pickle import *
from colorama import *

class Players(mp.Process):
    def __init__(self, numerojoueur, deck, main, printlock):
        super().__init__()
        self.numero = numerojoueur
        self.deck = deck
        self.cartesmain = main
        self.printlock = printlock

    def removecard(self, carte):
        self.cartesmain.remove(carte)

    def pioche(self, mqaffichage):
        cartepiochee = self.deck.get()
        cartepiochee.numerojoueur = self.numero
        self.cartesmain.append(cartepiochee)
        mqaffichage.send(str(1).encode(), type=4)

    def afficheHand(self):
        print("MAIN DU JOUEUR" + str(self.numero))
        nbdecartes = len(self.cartesmain)
        fin = " "
        couleur = Fore.RED
        for card in self.cartesmain:
            if card.couleur == "bleu":
                couleur = Fore.BLUE
            else:
                couleur = Fore.RED
            print(couleur + "╔═════════╗", end=fin)
        print("")
        for j in range(0, 7):
            for card in self.cartesmain:
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
        for card in self.cartesmain:
            if card.couleur == "bleu":
                couleur = Fore.BLUE
            else:
                couleur = Fore.RED
            if self.cartesmain.index(card)+1 < 10:
                print(couleur + "╚════"+str(self.cartesmain.index(card)+1)+"════╝", end=fin, flush=True)
            else:
                print(couleur + "╚════" + str(self.cartesmain.index(card) + 1) + "═══╝", end=fin, flush=True)
        print("" + Style.RESET_ALL)

    def affichageforce(self, mqaffichage):
        while True:
            _, _ = mqaffichage.receive(type=self.numero)
            with self.printlock:
                self.afficheHand()

    def run(self):
        mqcards = sysv_ipc.MessageQueue(100)
        mqverif = sysv_ipc.MessageQueue(self.numero)  # Message queue key numero joueur, sert à recevoir TRUE ou FALSE
        mqtouchejouee = sysv_ipc.MessageQueue(200 + self.numero)
        mqhandsize = sysv_ipc.MessageQueue(300)
        mqaffichage = sysv_ipc.MessageQueue(400)

        threadaffichage = threading.Thread(target=self.affichageforce, args=(mqaffichage, ))
        threadaffichage.start()

        while len(self.cartesmain) != 0 and not self.deck.empty():
            timer = multitimer.MultiTimer(interval=10, function=self.pioche, kwargs={"mqaffichage": mqaffichage}, runonstart=False)
            timer.start()
            erreur = True
            numcarte = 0
            while erreur:
                try:
                    bnumcarte, t = mqtouchejouee.receive()
                    numcarte = int(bnumcarte.decode())
                    mqcards.send(dumps(self.cartesmain[numcarte - 1]))
                    erreur = False
                except IndexError:
                    print("Joueur : " + str(self.numero) + " | Veuillez entrer une touche valide")
            timer.stop()
            blebool, t = mqverif.receive()
            lebool = blebool.decode() == 'True'
            if lebool:
                self.removecard(self.cartesmain[numcarte - 1])
                mqhandsize.send((str(len(self.cartesmain))).encode())
            else:
                self.pioche(mqaffichage)
        threadaffichage.join()

