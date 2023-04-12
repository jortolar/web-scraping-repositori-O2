import builtwith
from whois import whois
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import time
import csv
import os

'''
URLs d'interès del repositori O2 de la UOC:
    https://openaccess.uoc.edu/robots.txt
    https://openaccess.uoc.edu/sitemap
    https://openaccess.uoc.edu/pdf-sitemap.xml
'''

BASE_URL = 'https://openaccess.uoc.edu'
LANGUAGE = '?locale=ca'  # There are only 3 language options: ca, es, en
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
WAITING_TIME_BEFORE_ITEM_SCRAP = 0  # Time in seconds; the 0 value means no-time to wait
MAX_ITEMS_DEBUG = 10  # The web scrap ends when this limit is exceeded (debugging purposes only);
                      # the -1 value means no limit defined: all items will be scraped
CSV_FILE = f'{os.getcwd()}/uoc_o2_items.csv'
CSV_ENCODING = 'utf-8'


def show_buildwith_info() -> None:
    print(f'\n>> buildwith info\n{builtwith.parse(BASE_URL)}')


def show_whois_info() -> None:
    print(f'\n>> whois info\n{whois(BASE_URL)}')


def get_soap(url) -> BeautifulSoup:
    url = url[:-1] if url[-1] == '/' else url
    headers = {'User-Agent': USER_AGENT}
    page = requests.get(url + LANGUAGE, headers=headers)
    soup = BeautifulSoup(page.content, features='html.parser')
    return soup


def traverse_communities(url: str, items: list) -> list:
    soup = get_soap(url)
    communities = list()
    communities_raw = soup.find_all('h4', class_='list-group-item-heading-home')
    for community_raw in communities_raw:
        community = dict()
        community['name'] = community_raw.a.string
        community['url'] = BASE_URL + community_raw.a.get('href')
        hierarchy = list()
        hierarchy.append(community)
        traverse_subcommunities(community, hierarchy, items)
    return communities


def traverse_subcommunities(community: dict, hierarchy: list, items: list) -> list:
    soup = get_soap(community['url'])
    subcommunities_raw = soup.find_all('h4', class_='list-group-item-heading')
    if len(subcommunities_raw) > 0:
        for subcommunity_raw in subcommunities_raw:
            subcommunity = dict()
            name = subcommunity_raw.a.string
            url = BASE_URL + subcommunity_raw.a.get('href')
            subcommunity['url'] = url

            if name is not None:
                # Subcommunity
                subcommunity['name'] = name.strip()
            else:
                # Collection
                subcommunity['name'] = subcommunity_raw.a.span.text

            hierarchy.append(subcommunity)
            traverse_subcommunities(subcommunity, hierarchy, items)
            hierarchy.pop()
    else:
        items.extend(get_items(community, hierarchy))
        if MAX_ITEMS_DEBUG != -1 and get_item.counter >= MAX_ITEMS_DEBUG:
            print('\n>> end point debug')
            items_to_csv(items, CSV_FILE)
            exit(0)


def get_items(community: dict, hierarchy: list) -> list:
    soup = get_soap(community['url'])
    table = soup.find('table', class_='table')
    result = list()
    if table is not None:
        urls_raw = table.find_all('a')
        for url_raw in urls_raw:
            item_url = BASE_URL + url_raw.get('href')
            if 'handle' in item_url:
                time.sleep(WAITING_TIME_BEFORE_ITEM_SCRAP)
                result.append(get_item(item_url, hierarchy))
    return result


def get_item(url: str, hierarchy: list) -> dict:
    soup = get_soap(url)

    # Item info
    item = dict()
    attributes_raw = soup.find_all("td", class_=lambda value: value and value.startswith("metadataFieldLabel"))
    attributes = list()

    for attribute_raw in attributes_raw:
        if len(attribute_raw.get('class')) > 1:
            attributes.append(attribute_raw.get('class')[1])

    for attribute in attributes:
        if attribute in ('dc_contributor_author', 'dc_contributor_tutor'):
            authors = list()
            data_raw = soup.find('td', class_=f'metadataFieldValue {attribute}')
            authors_raw = data_raw.find_all('a')
            for author_raw in authors_raw:
                authors.append(author_raw.text)
            item[attribute] = authors
        elif attribute == 'dc_subject':
            subjects = list()
            data_raw = soup.find('td', class_=f'metadataFieldValue {attribute}')
            for subject_raw in data_raw:
                # skip <br/> <br> <br/> tags
                if isinstance(subject_raw, NavigableString):
                    if subject_raw.text != '':
                        subjects.append(subject_raw.text)
                elif isinstance(subject_raw, Tag):
                    for content in subject_raw.contents:
                        if content.text != '':
                            subjects.append(content.text)
            item[attribute] = subjects
        else:
            item[attribute] = soup.find('td', class_=f'metadataFieldValue {attribute}').text
    item['community_hierarchy'] = hierarchy

    # Item stats
    # ToDo: implementar al get_item_statistics l'obtenció d'estadístiques de l'item
    item_stats_raw = soup.find('a', class_='statisticsLink btn btn-info')
    item_stats_url = BASE_URL + item_stats_raw.get('href')
    item['statistics'] = get_item_statistics(item_stats_url)

    get_item.counter += 1
    print(f'\n>> item {get_item.counter}\n{item}')
    return item


def get_item_statistics(url: str) -> list:
    soup = get_soap(url)
    containers_raw = soup.find_all('div', class_='container')
    item_statistics = list()
    for container_raw in containers_raw:
        table_titles = container_raw.find_all('h4')
        table_contents = container_raw.find_all('table', class_='statsTable')
        if len(table_titles) == 0 or len(table_contents) == 0:
            continue
        table_titles.pop(0)

        # ToDo: implementar l'obtenció d'estadístiques de l'item

    return item_statistics


def items_to_csv(items: list, filename: str) -> None:
    keys = list()
    for item in items:
        for k in item.keys():
            if k not in keys:
                keys.append(k)
    with open(filename, 'w', newline='', encoding=CSV_ENCODING) as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(items)


items = list()
show_buildwith_info()
show_whois_info()
get_item.counter = 0
traverse_communities(BASE_URL, items)
items_to_csv(items, CSV_FILE)
