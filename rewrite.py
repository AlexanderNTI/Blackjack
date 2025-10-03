import pickle

def save_balance(money):
    import os
    script_dir = os.path.dirname(__file__); rel_path = "data/money.pkl"; money_pkl_path = os.path.join(script_dir, rel_path)

    with open(money_pkl_path, 'wb') as file:
        pickle.dump(money, file)

def load_balance():
    import os
    script_dir = os.path.dirname(__file__); rel_path = "data/money.pkl"; money_pkl_path = os.path.join(script_dir, rel_path)
    
    with open(money_pkl_path, 'rb') as file:
        money: float = pickle.load(file)
    return money

class Card:
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['\u2663', '\u2666', '\u2665', '\u2660'] # Clubs, Diamonds, Hearts, Spades
    points = { 
        '2': 2, '3': 3, '4': 4, '5': 5, 
        '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 
        'A': 11
    } 

    def __init__(self, rank: str, suit: str):
        self.suit = suit
        self.rank = rank
        self.value = Card.points[self.rank]

    def __str__(self):
        return f'[{self.rank}{self.suit}]'

class Deck:
    def __init__(self, amount: int):
        self.available_cards = []
        self.dealt_cards = []
        for _ in range(amount):
            for suit in Card.suits:
                for rank in Card.ranks:
                    self.available_cards.append(Card(rank, suit))

    def shuffle(self):
        import random
        random.shuffle(self.available_cards)

    def reset_deck(self):
        self.available_cards.extend(self.dealt_cards)
        self.dealt_cards.clear()
        self.shuffle()


    def deal_card(self) -> (Card | None):
        if self.available_cards:
            card = self.available_cards.pop()
            self.dealt_cards.append(card)
            return card
        else:
            return None


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            value += card.value
            if card.rank == 'A':
                aces += 1

        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21


    def is_bust(self):
        return self.get_value() > 21

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)
    
class Table:
    def __init__(self, deck_amount=4):
        self.deck = Deck(deck_amount)
        self.deck.shuffle()
        self.player_hands = []  # List of Hand objects for split support
        self.dealer_hand = Hand()
        self.balance = load_balance()
        self.bet = 0

    def new_round(self, bet):
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.bet = bet
        # Deal initial cards, only add if not None
        for _ in range(2):
            card = self.deck.deal_card()
            if card:
                self.player_hands[0].add_card(card)
        for _ in range(2):
            card = self.deck.deal_card()
            if card:
                self.dealer_hand.add_card(card)

    def player_turn(self):
        # Support for multiple hands (splits)
        i = 0
        while i < len(self.player_hands):
            hand = self.player_hands[i]
            doubled_down = False
            first_decision = True
            print(f"\n--- Playing Hand {i+1} ---")
            while True:
                print(f"Your hand: {hand} (value: {hand.get_value()})")
                print(f"Dealer shows: {self.dealer_hand.cards[0]}")
                if hand.is_blackjack():
                    print("Blackjack!")
                    break
                if hand.is_bust():
                    print("Bust!")
                    break
                opts = "(h)it, (s)tand"
                if first_decision and self.balance >= self.bet:
                    opts += ", (d)ouble down"
                if (first_decision and len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank and self.balance >= self.bet):
                    opts += ", s(p)lit"
                move = input(f"Choose action {opts}: ").lower()
                if move == 'h':
                    card = self.deck.deal_card()
                    if card:
                        hand.add_card(card)
                    else:
                        print("No more cards in the deck!")
                        break
                    first_decision = False
                elif move == 's':
                    break
                elif move == 'd' and first_decision and self.balance >= self.bet:
                    self.balance -= self.bet
                    self.bet *= 2
                    card = self.deck.deal_card()
                    if card:
                        hand.add_card(card)
                    else:
                        print("No more cards in the deck!")
                    print("Doubled down!")
                    doubled_down = True
                    break
                elif move == 'p' and first_decision and len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank and self.balance >= self.bet:
                    # Split: create new hand, move one card, deal one card to each
                    self.balance -= self.bet
                    new_hand = Hand()
                    split_card = hand.cards.pop()
                    new_hand.add_card(split_card)
                    card1 = self.deck.deal_card()
                    card2 = self.deck.deal_card()
                    if card1:
                        hand.add_card(card1)
                    if card2:
                        new_hand.add_card(card2)
                    self.player_hands.append(new_hand)
                    print("Hand split!")
                    break  # Play this hand from the start
                else:
                    print("Invalid input.")
                first_decision = False
            i += 1

    def dealer_turn(self):
        print(f"\nDealer's hand: {self.dealer_hand} (value: {self.dealer_hand.get_value()})")
        while self.dealer_hand.get_value() < 17:
            card = self.deck.deal_card()
            if card:
                self.dealer_hand.add_card(card)
                print(f"Dealer hits: {self.dealer_hand} (value: {self.dealer_hand.get_value()})")
            else:
                print("No more cards in the deck!")
                break
        if self.dealer_hand.is_bust():
            print("Dealer busts!")
        else:
            print(f"Dealer stands at {self.dealer_hand.get_value()}")

    def settle_bet(self):
        dealer_val = self.dealer_hand.get_value()
        for idx, hand in enumerate(self.player_hands):
            player_val = hand.get_value()
            print(f"\n--- Result for Hand {idx+1} ---")
            if hand.is_bust():
                print("You lose!")
                self.balance -= self.bet
            elif self.dealer_hand.is_bust() or player_val > dealer_val:
                print("You win!")
                self.balance += self.bet
            elif player_val == dealer_val:
                print("Push.")
            else:
                print("You lose!")
                self.balance -= self.bet
        save_balance(self.balance)

    def show_balance(self):
        print(f"Current balance: ${self.balance}")

def main():
    print("Welcome to Blackjack!")
    table = Table(deck_amount=4)
    while True:
        table.show_balance()
        # Get bet
        while True:
            try:
                bet = int(input("Enter your bet: "))
                if bet > table.balance or bet <= 0:
                    print("Invalid bet amount.")
                else:
                    break
            except ValueError:
                print("Please enter a valid number.")
        table.new_round(bet)
        table.player_turn()
        table.dealer_turn()
        table.settle_bet()
        again = input("Play again? (y/N): ").strip().lower()
        if again != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()