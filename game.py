import random as rnd
import logging

# import pytest as test
TEST_NAMES = ['Noord', 'Oost', 'Zuid', 'West']
SIGNS = ['klaver', 'schoppen', 'harten', 'ruiten']
KEYS = [7, 8, 9, 10, 'boer', 'vrouw', 'heer', 'aas']
VALS = [0, 0, 0, 10, 2, 3, 4, 11]
VALS_TROEF = {'7': 0, '8': 0, '9': 14, '10': 10, 'boer': 20, 'vrouw': 3, 'heer': 4, 'aas': 11}

logging.basicConfig(filename="klaver.log", level="DEBUG")


class Card(object):
    def __init__(self, symbol, number, value=0, order=None):
        self.symbol = symbol
        self.number = number
        self.value = value
        self.order = order

    def check_value(self, number='0'):
        if self.number in ['7', '8', '9']:
            self.value = 0
        elif self.number == '10':
            self.value = 10
        elif self.number == 'boer':
            self.value = 2
        elif self.number == 'vrouw':
            self.value = 3
        elif self.number == 'heer':
            self.value = 4
        elif self.number == 'aas':
            self.value = 11
        return self.value

    def troef_update(self, troef):
        if self.symbol == troef:
            if self.number == 9:
                self.value = 14
            elif self.number == 'boer':
                self.value = 20


    def __repr__(self):
        return '{} {}'.format(self.symbol, self.number)


class Team(object):
    def __init__(self, player1, player2):
        self.score = []
        self.roem = []
        self.team = [player1, player2]
        self.subtotal = []

    def add_tussenscore(self, score, roem=0):
        self.score.append(score)
        self.roem.append(roem)

    def show_score(self, team2,):
        self.scorelist = '{}\t  {}\n'.format(self.team, team2.team)
        for i in range(len(self.score)):
            self.scorelist += ' {}  \t{}\t\t{}\t{}\n'.format(self.score[i], self.roem[i], team2.score[i], team2.roem[i])
        print('{}'.format(self.scorelist))

    def sum_scores_and_reset(self, team2):
        self.subtotal.append(sum(self.score) + sum(self.roem))
        print(self.subtotal)
        self.score = []
        self.roem = []

    def __repr__(self):
        return str(self.team)


class Player(object):
    def __init__(self, name, number):
        self.name = name
        self.hand = []
        self.deal = False
        self.dummy = True
        self.number = number  # 0=N, 1=O, 2=Z, 3=W

    def dummy_play(self, stack):
        card = None
        if len(stack) > 0:
            for eachcard in self.hand:
                if stack[0].symbol == eachcard.symbol:  # check rule
                    card = eachcard
                else:
                    card = self.hand[0]
        else:
            # print(self.hand)
            card = self.hand[0]
        self.find_and_remove(card)
        return card

    def human_play(self):
        print('Je hebt deze kaarten: {}'.format(self.hand))
        ask = input('Kies welke kaart je op wilt leggen: \n').split()
        for card in self.hand:
            if card.symbol == ask[0] and str(card.number) == ask[1]:
                print('val ', card.value)
                self.find_and_remove(card)
                return card

    def find_and_remove(self, card):
        try:
            c = 0
            while c in range(len(self.hand)):
                if (self.hand[c].symbol == card.symbol
                        and self.hand[c].number == card.number
                        and self.hand[c].value == card.value):
                    order = self.hand[c].order
                    del self.hand[c]
                    return order
                else:
                    c += 1
        except AttributeError as e:
            print('Die kaart heb je niet!')
            return self.human_play()

    def get_cards(self, gam, n):
        [self.hand.append(card) for card in gam.deck[0:n]]
        del gam.deck[0:n]
        # print('dealer: ', self.hand)

    def deal_cards(self, gam, n):
        for player in gam.players:
            cards = gam.deck[0:n]
            if not player.deal:
                [player.hand.append(card) for card in cards]
                del gam.deck[0:n]
                # print(player.name, ': ', player.hand)
        self.get_cards(gam, n)

    def update_hand(self, troef):
        for card in self.hand:
            if card.symbol == troef:
                card.troef_update(troef)
                #  card.value = VALS_TROEF[card.number]
        logging.debug('Player {} updated hand: {}'.format(self.name, [card.value for card in self.hand]))

    def sort_hand(self):
        self.hand.sort(key=lambda card: card.symbol)

    def __repr__(self):
        return '{}'.format(self.name)


class Game(object):
    def __init__(self):
        self.deck = []
        self.players = []
        self.names = input('Wie spelen er? N O Z W \n').split()
        for i in range(4):
            self.players.append(Player(self.names[i], i))
        self.order = []
        self.dealerid = 0
        self.troef = None
        self.players[0].dummy = False
        self.dealer = self.players[self.dealerid]
        self.stack = []
        self.teams = [Team(self.players[0], self.players[2]), Team(self.players[1], self.players[3])]
        print('De teams zijn: ', self.teams[0].team, 'en ', self.teams[1].team)

    def make_deck(self, test=False):
        for sign in SIGNS:
            for i in range(len(KEYS)):
                self.deck.append(Card(sign, KEYS[i], VALS[i], order=i))
        if test:
            pass
        else:
            rnd.shuffle(self.deck)

    def determine_dealer(self):
        self.dealer.deal = True # TODO: make sure the next player is the dealer
        print('De deler is {}'.format(self.dealer.name))
        self.dealer.deal_cards(self, 3)
        self.dealer.deal_cards(self, 2)
        self.dealer.deal_cards(self, 3)

    def determine_order(self):
        if self.dealerid == 0:
            self.order = [1, 2, 3, self.dealerid]
        elif self.dealerid == 1:
            self.order = [2, 3, 0, self.dealerid]
        elif self.dealerid == 2:
            self.order = [3, 0, 1, self.dealerid]
        elif self.dealerid == 3:
            self.order = [0, 1, 2, self.dealerid]
        print('Player order: {}'.format([self.players[self.order[i]] for i in range(4)]))

    def pick_troef(self, id):
        """ Ask the player with id dealerid + 1 for the troef"""
        troef_picker = self.players[id]
        if troef_picker.dummy:
            self.troef = rnd.choice(SIGNS)
            logging.debug('{} picked {} as troef'.format(troef_picker, self.troef))
        else:
            troef = input("Kies je troef (k s r h): ")
            if troef.startswith('k'):
                self.troef = 'klaver'
            elif troef.startswith('s'):
                self.troef = 'schoppen'
            elif troef.startswith('r'):
                self.troef = 'ruiten'
            elif troef.startswith('h'):
                self.troef = 'harten'
        print("{} is troef".format(self.troef))

    def play_slag(self):
        self.determine_order()
        for i in range(4):  # loop over each player 4 times to check their order number
            for player in self.players:
                if player.number == self.order[i]:
                    if player.dummy:
                        card = player.dummy_play(self.stack)
                    else:
                        player.sort_hand()
                        card = player.human_play()
                    self.stack.append(card)
                    logging.debug('Player {} played a {}'.format(player.name, card))
            print(self.stack)
        self.check_score()
        self.dealerid = (self.dealerid + 1) % 4
        logging.debug('dealer id is {}'.format(self.dealerid))

    def play(self):
        """ should handle troef and call play_slag() until everyone's hands are empty"""
        troef_id = 1
        for i in range(4):
            self.make_deck()
            self.determine_dealer()
            self.pick_troef(troef_id)
            for player in self.players:
                player.update_hand(self.troef)
                # print([card.value for card in player.hand])

            for i in range(8):
                self.play_slag()
            self.check_nat(troef_id)
            self.teams[0].sum_scores_and_reset(self.teams[1])
            print('Team {} heeft {} punten, team {} {}.'.format(self.teams[0], self.subtotal[-1], team2.team,
                                                                team2.subtotal[-1]))

            troef_id = (troef_id + 1) % 4


    def check_score(self):
        total_value = 0
        winnercard = self.stack[0]
        winner = self.players[self.order[0]]
        for i in range(len(self.stack)):
            if self.stack[i].symbol == winnercard.symbol and self.stack[i].value >= winnercard.value:
                winner = self.players[self.order[i]]
                winnercard = self.stack[i]
                logging.debug(winnercard)
            elif self.stack[i].symbol == self.troef:
                logging.debug('{} encountered'.format(self.stack[i]))
                if winnercard.symbol == self.troef:  # to check if the previous winner was already troef
                    if self.stack[i].value > winnercard.value:
                        winner = self.players[self.order[i]]
                        winnercard = self.stack[i]
                        logging.debug('winner card is {}'.format(winnercard))
                else:
                    winner = self.players[self.order[i]]  # TODO: dit moet anders, zo wordt een winnaar overschreven
                    winnercard = self.stack[i]
            else:
                logging.debug('if statement false:')
            total_value += self.stack[i].value
        print('the winner card is {}'.format(winnercard))
        roem = self.check_roem()
        self.stack = []
        for team in self.teams:
            if winner in team.team:
                team.add_tussenscore(total_value, roem)
            else:
                team.add_tussenscore(0, 0)
        self.teams[0].show_score(self.teams[1])

    def check_nat(self, id):
        """ Being NAT means that your team picked troef but failed to get more than half of the total score including
        roem. This sets their score for that slag to 0 and gives all of their roem and points to the other team.
        e.g. without roem it's the sum of the deck's values (162). This function first determines the 'total score
        before asserting if the picking team has fulfilled its target."""
        total_score = 0
        for team in self.teams:
            total_score += sum(team.score[-1])  #
            total_score += sum(team.roem[-1])
        logging.debug('Total score this round is {}'.format(total_score))

        for i in range(len(self.teams)):
            if self.players[id] in self.teams[i].team:
                if self.teams[i].subtotal < total_score:
                    print('Oh oh! Team {} is nat! De punten van deze ronde gaan naar het andere team...'.format(self.teams[i]))
                    self.teams[i].subtotal[-1] = 0 #FIXME: niet de laatste score, maar die van alle 8 slagen gaat naar de ander
                    self.teams[(i+1) % 2].subtotal[-1] = total_score


    def check_roem(self):
        roem = 0
        sign_dict = {'klaver': [], 'schoppen': [], 'harten': [], 'ruiten': []}
        for card in self.stack:
            sign_dict[card.symbol].append(card.order)
        # three and four in a row
        for sym in sign_dict.keys():
            for i in range(5):
                if i in sign_dict[sym] and i+1 in sign_dict[sym] and i+2 in sign_dict[sym]:
                    if i+3 < 8 and i+3 in sign_dict[sym]:
                        roem += 30  # normally it's 50, but this is a loophole to get 50, bc the else always triggers.
                    else:
                        roem += 20
            # koningspaar
            if sym == self.troef:
                if 5 in sign_dict[sym] and 6 in sign_dict[sym]:
                    roem += 20
        return roem

    def forge_state(self, stack):
        self.players = [Player(TEST_NAMES[i], i) for i in range(4)]
        self.deck = []
        self.order = [0, 1, 2, 3]
        self.make_deck(test=True)
        self.stack = stack
        assert self.check_score()


if __name__ == '__main__':
    game = Game()
    # game.forge_state([Card('ruiten', 'aas', 11), Card('harten',7, 0), Card('ruiten', 10, 10), Card('ruiten', 'boer', 2)])
    #  print(game.deck)
    game.play()