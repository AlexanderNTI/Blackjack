import pickle, os

script_dir = os.path.dirname(__file__)
rel_path = "data\money.pkl"
money_pkl_path = os.path.join(script_dir, rel_path)

with open(money_pkl_path, 'rb') as file:
        money = pickle.load(file)
        print(f'Balance: {money}$')

money = int(input('Set your balance: '))

with open(money_pkl_path, 'wb') as file:
        pickle.dump(money, file)
