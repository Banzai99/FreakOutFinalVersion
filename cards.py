from colorama import *


class Cards:
    def __init__(self, numero, couleur):
        self.numero = numero
        self.couleur = couleur
        self.numerojoueur = -1

    def __str__(self):
        if self.couleur == "bleu":
            cardstring = Fore.BLUE + "╔════════╗\n" \
                                     "║        ║\n" \
                                     "║        ║\n" \
                                     "║        ║\n" \
                                     "║        ║\n" \
                                     "║        ║\n" \
                                     "╚════════╝\n" + Style.RESET_ALL
        else:
            cardstring = Fore.RED + "╔════════╗\n" \
                                                 "║        ║\n" \
                                                 "║        ║\n" \
                                                 "║        ║\n" \
                                                 "║        ║\n" \
                                                 "║        ║\n" \
                                                 "╚════════╝\n" + Style.RESET_ALL
        return cardstring
