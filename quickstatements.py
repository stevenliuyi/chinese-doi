import pandas as pd
import re


def add_short_title(df):
    df['short_title'] = df['title'].apply(
        lambda x: re.sub(r'[^\u4e00-\u9fff]', '', x)[:10])


def write_to_file(journal_qid, df_merged):
    df_qs = pd.DataFrame({
        'qid':
        df_merged['qid'],
        'P356':
        df_merged['doi'].apply(lambda x: f'"{x.upper()}"')
    })

    filename = f'{journal_qid}_qs.csv'
    df_qs.to_csv(filename, index=False)
    print(f'{filename} is saved!')


def main(journal_qid):
    doi_filename = f'{journal_qid}_filtered.csv'
    df_doi = pd.read_csv(doi_filename, dtype={'issue': 'str'})
    add_short_title(df_doi)

    qid_filename = f'{journal_qid}_items.csv'
    df_qid = pd.read_csv(qid_filename, dtype={'issue': 'str'})
    add_short_title(df_qid)

    df_merged = df_qid.merge(df_doi, on=['short_title', 'year', 'issue'])
    write_to_file(journal_qid, df_merged)


if __name__ == '__main__':
    import sys
    journal_qid = sys.argv[1]
    main(journal_qid)