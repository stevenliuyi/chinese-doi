from web_request import web_request
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
import os.path
from shutil import copyfile


def relative_path(base, path):
    return f"{'/'.join(base.split('/')[:-1])}/{path}"


def get_issues(summary_url, journal_type):
    summary_page = web_request(summary_url)
    soup = BeautifulSoup(summary_page.content, 'html.parser')

    if journal_type == 1:
        issues = soup.find_all('a', {'href': re.compile(r'\.\.\/volumn.*')})
    elif journal_type == 2:
        issues = soup.find_all('a', {'href': re.compile(r'.*issue_list.*')})

    issue_urls = [
        relative_path(summary_url, issue.get('href')) for issue in issues
    ]
    issue_urls = list(set(issue_urls))  # remove duplicates

    return issue_urls


#def format_authors(authors):
#    authors = authors.replace('\t', ';')
#    authors = re.sub(r'[,;，；]\s*', ';', authors)
#    authors = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1;\2',
#                     authors)
#    authors = re.sub(r'\d', '', authors)
#
#    return authors


def format_issue(issue):
    issue = issue.upper()
    issue = re.sub(r'[-Z]', 'S', issue)
    if issue in ['S', '增刊']: issue = 'S1'

    return issue.zfill(2)


def get_article(article_elem, issue_url, year, issue, journal_type):
    if journal_type == 1:
        title_elem = article_elem.find('a', class_='biaoti')
        if title_elem is None:
            title_elem = article_elem.find('p', class_='index_txt1').find('a')
        title = title_elem.text
        #authors = format_authors(
        #    article_elem.find('dd', class_='zuozhe').text)
        link = article_elem.find('a',
                                 {'href': re.compile(r'https://doi\.org.*')})
        doi = '' if link is None else link.get('href')[16:]
    elif journal_type == 2:
        title = article_elem.text
        link = relative_path(issue_url, article_elem.get('href'))
        article_page = web_request(link)
        soup = BeautifulSoup(article_page.content, 'html.parser')
        doi_elem = soup.find('span', id='DOI')
        doi = '' if doi_elem is None or doi_elem.find(
            'a') is None else doi_elem.find('a').text

    article = {
        'year': year.strip(),
        'issue': issue.strip(),
        'title': title.strip().replace('\n', '').replace('\r', ''),
        'doi': doi.strip()
    }
    print(article)

    return article


def get_issue(issue_url, journal_type):
    issue_page = web_request(issue_url)
    soup = BeautifulSoup(issue_page.content, 'html.parser')
    print(issue_url)

    # find year and issue number
    if journal_type == 1:
        year_volume_issue_elem = soup.find(
            class_=re.compile(r'(njq|gkyllb_qi)'))
        year_volume_issue = year_volume_issue_elem.text
        year = re.search(r'(\d+)年', year_volume_issue).group(1)
        #volume = re.search(r'第(\d+)卷', year_volume_issue).group(1)
        issue = re.search(r'第(\S*\d*)期', year_volume_issue).group(1)
    elif journal_type == 2:
        year_volume_issue = soup.find(class_='STYLE2',
                                      text=re.compile(r'.*年第.*[卷巻].*期.*')).text
        year = re.search(r'(\d+)年', year_volume_issue).group(1)
        issue = re.search(r'[卷巻年]第([^卷]*\d*)期', year_volume_issue).group(1)

    issue = format_issue(issue)

    # find article elements
    if journal_type == 1:
        article_elems = soup.find_all(
            class_=re.compile(r'(wenzhang|index_tab_licont)'))
    elif journal_type == 2:
        article_elems = filter(
            lambda x: x.text != '摘要',
            soup.find_all('a', {'href': re.compile(r'view_abstract\.aspx.*')}))

    articles = [
        get_article(article_elem, issue_url, year, issue, journal_type)
        for article_elem in article_elems
    ]

    return articles


def write_to_file(journal_qid, articles, overwrite_file):
    filename = f'{journal_qid}_full.csv'
    if (not overwrite_file) and os.path.isfile(filename):
        backup_filename = f'{journal_qid}_full_backup.csv'
        copyfile(filename, backup_filename)
        print(f'{filename} already exists! Renamed as {backup_filename}.')

    csvfile = open(filename, 'w')
    writer = csv.writer(csvfile)
    writer.writerow(['year', 'issue', 'title', 'doi'])
    for article in articles:
        writer.writerow([
            article['year'], article['issue'], article['title'], article['doi']
        ])

    csvfile.close()
    print(f'{filename} is saved!')


def main(journal_qid, overwrite_file=False, existing_file=False):
    # check if file already exists
    filename = f'{journal_qid}_full.csv'
    if os.path.isfile(filename) and existing_file:
        print(f'{filename} already exists and will be used.')
        return

    # journal information
    df_journals = pd.read_csv('journals.csv')
    journal = df_journals[df_journals['journal'] == journal_qid]
    if (journal.empty):
        print(f'Cannot find information for journal {journal_qid}')
        exit()

    url = journal.url.array[0]
    journal_type = journal.type.array[0]

    issue_urls = get_issues(url, journal_type)

    articles = []
    for issue_url in issue_urls:
        articles += get_issue(issue_url, journal_type)

    write_to_file(journal_qid, articles, overwrite_file)


if __name__ == '__main__':
    import sys
    journal_qid = sys.argv[1]
    main(journal_qid)