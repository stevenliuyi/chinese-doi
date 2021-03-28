from web_request import web_request
import pandas as pd
import os
from shutil import copyfile


def check(doi, status):
    print(doi)

    doi_url = f'https://doi.org/{doi}'
    status_code = web_request(doi_url).status_code

    if status_code == 200:
        return True
    elif status_code == 404:
        return False
    else:
        status['doi'].append(doi)
        status['status_code'].append(status_code)
        return False


def main(journal_qid,
         validate_doi=True,
         overwrite_file=False,
         incomplete_file=True,
         existing_file=False):
    nonfiltered_filename = f'{journal_qid}_full.csv'
    incomplete_filename = f'{journal_qid}_filtered_incomplete.csv'
    filename = f'{journal_qid}_filtered.csv'

    # check if file already exists
    if os.path.exists(filename) and existing_file:
        print(f'{filename} already exists and will be used.')
        return

    if not (incomplete_file and os.path.isfile(incomplete_filename)):
        df = pd.read_csv(nonfiltered_filename, dtype={'issue': 'str'})
    else:
        print(
            f'Last run was incomplete. Continue from {incomplete_filename}...')
        df = pd.read_csv(incomplete_filename, dtype={'issue': 'str'})

    # filter out articles without DOI
    df = df[df.notnull().doi]

    if validate_doi:
        status = {'doi': [], 'status_code': []}

        invalid_dois = []
        for doi in df['doi']:
            try:
                if not check(doi, status): invalid_dois.append(doi)
            except:
                print('Error encountered when validating DOIs!')
                df = df[~df['doi'].isin(invalid_dois)]
                df.to_csv(incomplete_filename, encoding='utf-8', index=False)
                print(f'{incomplete_filename} is saved.')
                exit(1)

        df = df[~df['doi'].isin(invalid_dois)]

        df_status = pd.DataFrame(status)
        if df_status.shape[0] > 0:
            filename_status = f'{journal_qid}_unknown_status_codes.csv'
            print(
                f'Encountered unknown status codes when validating DOIs! Saved to {filename_status}.'
            )
            df_status.to_csv(filename_status, index=False)

    if (not overwrite_file) and os.path.isfile(filename):
        backup_filename = f'{journal_qid}_filtered_backup.csv'
        copyfile(filename, backup_filename)
        print(f'{filename} already exists! Renamed as {backup_filename}.')

    df.to_csv(filename, encoding='utf-8', index=False)
    print(f'{filename} is saved!')

    if os.path.isfile(incomplete_filename):
        os.remove(incomplete_filename)
        print(f'Incomplete file {incomplete_filename} is deleted.')


if __name__ == '__main__':
    import sys
    journal_qid = sys.argv[1]
    main(journal_qid)
