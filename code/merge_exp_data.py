import pandas as pd

honesty_versions = ['2024-05-24', '2024-06-17', '2024-07-02']
trust_versions = ['2024-05-25', '2024-06-18', '2024-07-03']
giftex_versions = ['2024-05-25', '2024-06-18', '2024-07-02']

def merge_data(exp, versions):
    for type in ['participants', 'rounds']:
        data = pd.DataFrame()        
        for version in versions:
            ver = pd.read_csv(f'data/generated/{exp}_{version}_{type}.csv', index_col= False)
            data = pd.concat([data, ver])

        data.to_csv(f'data/generated/{exp}_merged_{type}.csv', index = False)


merge_data('honesty', honesty_versions)
merge_data('trust', trust_versions)
merge_data('giftex', giftex_versions)