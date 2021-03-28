import requests
import urllib.parse
import pandas as pd


def main(journal_qid):
    sparql_query = """
    SELECT ?article (year(?date) as ?year) ?issue ?title
    WHERE
    {
      ?article wdt:P31 wd:Q13442814;
               wdt:P1433 wd:""" + journal_qid + """;
               wdt:P1476 ?title;
               wdt:P577 ?date;
               wdt:P433 ?issue .
      MINUS { ?article wdt:P356 ?doi . }
      FILTER(LANG(?title) = 'zh') .
    }
"""
    sparql_query = urllib.parse.quote_plus(sparql_query)
    query_url = f'https://query.wikidata.org/sparql?format=json&query={sparql_query}'
    res = requests.get(query_url).json()
    articles = [{
        'qid': x['article']['value'][31:],
        'year': x['year']['value'],
        'issue': x['issue']['value'],
        'title': x['title']['value']
    } for x in res['results']['bindings']]
    df = pd.DataFrame(articles)

    filename = f'{journal_qid}_items.csv'
    df.to_csv(filename, encoding='utf-8', index=False)
    print(f'{filename} is saved!')


if __name__ == '__main__':
    import sys
    journal_qid = sys.argv[1]
    main(journal_qid)