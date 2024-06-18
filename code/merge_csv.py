import pandas as pd

csv1 = pd.read_csv("data/giftex_otree_2024-06-18a.csv")
csv2 = pd.read_csv("data/giftex_otree_2024-06-18b.csv")

final_csv = pd.concat([csv1, csv2])
final_csv.to_csv("data/giftex_otree_2024-06-18.csv")