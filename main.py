import argparse
from journal_doi import main as journal_doi
from filter_doi import main as filter_doi
from wd_items import main as wd_items
from quickstatements import main as quickstatements

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('qid', help='journal QID')  # example: Q98517082
    parser.add_argument('-j',
                        '--get-journal-doi',
                        action='store_true',
                        help='obtain DOIs from the journal')
    parser.add_argument('-f',
                        '--filter-doi',
                        action='store_true',
                        help='filter out empty or invalid DOIs')
    parser.add_argument(
        '-w',
        '--wikidata-items',
        action='store_true',
        help='obtain Wikidata items of articles from the journal')
    parser.add_argument('-q',
                        '--quickstatements',
                        action='store_true',
                        help='generate QuickStatements commands')
    parser.add_argument('-a',
                        '--all',
                        action='store_true',
                        help='execute the whole process')
    parser.add_argument('--no-validation',
                        action='store_true',
                        help='skip validating DOIs')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='overwrite existing output files')
    parser.add_argument(
        '--use-existing-file',
        action='store_true',
        help='skip generating output files when they already exist')
    parser.add_argument(
        '--ignore-incomplete-file',
        action='store_true',
        help='ignore incomplete output files and create new one from scratch')

    args = parser.parse_args()

    if args.get_journal_doi or args.all:
        print("Obtaining DOIs from the journal's website...")
        journal_doi(args.qid,
                    overwrite_file=args.overwrite,
                    existing_file=args.use_existing_file)

    if args.filter_doi or args.all:
        print('Filtering DOIs...')
        filter_doi(args.qid,
                   validate_doi=not args.no_validation,
                   overwrite_file=args.overwrite,
                   incomplete_file=not args.ignore_incomplete_file,
                   existing_file=args.use_existing_file)

    if args.wikidata_items or args.all:
        print('Obtaining Wikidata items of articles from the journal...')
        wd_items(args.qid)

    if args.quickstatements or args.all:
        print('Generating QuickStatements commands...')
        quickstatements(args.qid)