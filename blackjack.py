import pickle

class Card:
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['\u2663', '\u2666', '\u2665', '\u2660'] # Clubs, Diamonds, Hearts, Spades
    blackjack_values = { 
        '2': 2, '3': 3, '4': 4, '5': 5, 
        '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 
        'A': (11, 1)
    } 

    def __init__(self, rank: str, suit: str):
        self.suit = suit
        self.rank = rank
        self.value = Card.blackjack_values[self.rank]

    def __str__(self):
        return f'[{self.rank}{self.suit}]'

class Deck:
    def __init__(self, amount: int):
        self.availableCards = []
        self.dealtCards = []
        for _ in range(amount):
            for suit in Card.suits:
                for rank in Card.ranks:
                    self.availableCards.append(Card(rank, suit))

    def shuffle(self):
        import random
        random.shuffle(self.availableCards)

    def reset_deck(self):
        self.availableCards.extend(self.dealtCards)
        self.dealtCards.clear()
        self.shuffle()

    def deal_card(self) -> (Card | None):
        if self.availableCards:
            card = self.availableCards.pop()
            self.dealtCards.append(card)
            return card
        else:
            return None

    def get_size(self):
        return len(self.availableCards)

def print_table(hands: list[list[Card]], selectedHand: int):
    print('\n\nDealer\'s hand:')
    for card in hands[0]:
        print(card, end=' ')
    print('\n')
    print('Your hand(s):')
    for hand in hands[1:]:
        if hands.index(hand) == selectedHand:
            print('>', end=' ')
        for card in hand:
            print(card, end=' ')
        if hand == hands[-1]:
            print()
        else:
            print('\n')

def check_score(hand: list[Card], hardScore: bool):
    score = 0
    for card in hand:
        if card.rank != 'A': 
            score += card.value
        else:
            if hardScore == True:
                score += card.value[1]
            else:
                continue
    if hardScore == False:
        for card in hand:
            if card.rank == 'A':
                if score + card.value[0] > 21:
                    score += card.value[1]
                else:
                    score += card.value[0]
            else:
                continue
    return score


def betting(money):
    print(f'You have {money}$ in your bank account')
    while True:
        bet = int(input('Choose betting amount: '))
        if bet > money:
            print('Invalid amount')
        else:
            break
    return bet

def get_decision(hand: list, deck: Deck, turn: bool, firstDecision: bool, hands: list[list]):
    invalid = False
    doubleDown = False
    while True:
        if invalid == True:
            print("Invalid option, try again:", end=" ")
            invalid = False
        else:
            print("Select your decision (h/s/d/sp):", end=" ")
        decision = input().lower()
        if decision == 'h':
            hand.append(deck.deal_card())
            firstDecision = False
            break
        elif decision == 's':
            turn = False
            break
        elif decision == 'd' and firstDecision == True:
            hand.append(deck.deal_card())
            doubleDown = True
            turn = False
            break
        elif decision == 'sp' and hand[0].rank == hand[1].rank and firstDecision == True:
            hands.append([])
            split_card = hand.pop()
            hands[-1].append(split_card)
            hand.append(deck.deal_card())
            hands[-1].append(deck.deal_card())
            break
        else:
            invalid = True

    return turn, firstDecision, doubleDown

def save_balance(money):
    import os
    script_dir = os.path.dirname(__file__); rel_path = "data\money.pkl"; money_pkl_path = os.path.join(script_dir, rel_path)

    with open(money_pkl_path, 'wb') as file:
        pickle.dump(money, file)

def blackjack(ruleH17: bool, deckAmount: int):
    import os
    script_dir = os.path.dirname(__file__); rel_path = "data\money.pkl"; money_pkl_path = os.path.join(script_dir, rel_path)
    
    with open(money_pkl_path, 'rb') as file:
        money: int = pickle.load(file)
    shoe = Deck(deckAmount); shoe.shuffle()

    while True:
        dealer_hand, player_hand  = [], []; hands = [dealer_hand, player_hand]
        natural, double_down = [], []
        outcome = 0
        bet = betting(money)
        
        for _ in range(2):
            player_hand.append(shoe.deal_card())
        dealer_hand.append(shoe.deal_card())

        for hand in hands[1:]:
            turn, first_decision, double = True, True, False
            if check_score(hand, False) == 21:
                natural.append(hands.index(hand))
                continue
            while turn == True:
                print_table(hands, hands.index(hand))
                turn, first_decision, double = get_decision(hand, shoe, turn, first_decision, hands)
                if double == True:
                    double_down.append(hands.index(hand))
                if check_score(hand, False) > 21:
                    break
        
        dealer_hand.append(shoe.deal_card())
        if ruleH17 == True:
            while check_score(dealer_hand, True) < 17:
                dealer_hand.append(shoe.deal_card())
        else:
            while check_score(dealer_hand, False) < 17:
                dealer_hand.append(shoe.deal_card())

        print_table(hands, -1)
        
        for hand in hands[1:]:
            if 21 >= check_score(hand, False) > check_score(dealer_hand, False) or check_score(dealer_hand, False) > 21 >= check_score(hand, False): # Check for win
                if hands.index(hand) in double_down:
                    outcome += bet * 2
                elif hands.index(hand) in natural:
                    outcome += bet * 1.5
                else:
                    outcome += bet
            elif check_score(hand, False) > 21 or 21 >= check_score(dealer_hand, False) > check_score(hand, False): # Check for loss
                if hands.index(hand) in double_down:
                    outcome -= bet * 2
                else:
                    outcome -= bet
            elif 21 >= check_score(hand, False) == check_score(dealer_hand, False): # Check for push
                outcome += 0
        money += outcome
        save_balance(money)

        if outcome >= 0:
            print(f'You won {outcome}$')
        elif outcome < 0:
            print(f'You lost {outcome}$')

        play_again = input('Do you want to play again? (y/N): ').lower()
        if play_again == 'n':
            break
        elif play_again == 'y':
            if shoe.get_size() <= 35:
                shoe.reset_deck()
        else:
            break


if __name__ == "__main__":
    blackjack(True, 4)