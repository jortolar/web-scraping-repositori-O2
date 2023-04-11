import builtwith
from whois import whois
import requests
from bs4 import BeautifulSoup

base_url = 'https://openaccess.uoc.edu'
language = '?locale=ca'  # There are only 3 language options: ca, es, en
items = list()


def show_buildwith_info() -> None:
    print(f"\n>> buildwith info\n{builtwith.parse(base_url)}")


def show_whois_info() -> None:
    print(f"\n>> whois info\n{whois(base_url)}")


def get_soap(url) -> BeautifulSoup:
    url = url[:-1] if url[-1] == '/' else url
    page = requests.get(url + language)
    soup = BeautifulSoup(page.content, features='html.parser')
    return soup


def traverse_communities(url: str, items: list) -> list:
    soup = get_soap(url)
    communities = list()
    communities_raw = soup.find_all('h4', class_='list-group-item-heading-home')
    for community_raw in communities_raw:
        community = dict()
        community['name'] = community_raw.a.string
        community['url'] = base_url + community_raw.a.get('href')
        traverse_subcommunities(community, items)
    return communities


def traverse_subcommunities(community: dict, items: list) -> list:
    soup = get_soap(community['url'])
    subcommunities_raw = soup.find_all('h4', class_='list-group-item-heading')
    if len(subcommunities_raw) > 0:
        for subcommunity_raw in subcommunities_raw:
            subcommunity = dict()

            name = subcommunity_raw.a.string
            url = base_url + subcommunity_raw.a.get('href')
            subcommunity['url'] = url

            if name is not None:
                # Subcommunity
                subcommunity['name'] = name.strip()
            else:
                # Collection
                subcommunity['name'] = subcommunity_raw.a.span.text

            traverse_subcommunities(subcommunity, items)
    else:
        get_items(community)


def get_items(community: dict) -> list:
    soup = get_soap(community['url'])
    items = list()
    table = soup.find('table', class_='table')
    if table is not None:
        urls_raw = table.find_all('a')
        for url in urls_raw:
            if 'handle' in url.get('href'):
                items.append(get_item(base_url + url.get('href')))


def get_item(url: str) -> dict:
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
                # skip <br/> tags
                if subject_raw.text != '':
                    subjects.append(subject_raw.text)
            item[attribute] = subjects
        else:
            item[attribute] = soup.find('td', class_=f'metadataFieldValue {attribute}').text

    # Item stats
    # ToDo: implementar al get_item_statistics l'obtenció d'estadístiques de l'item
    item_stats_raw = soup.find('a', class_='statisticsLink btn btn-info')
    stats_url = base_url + item_stats_raw.get('href')
    item['statistics'] = get_item_statistics(stats_url)

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


show_buildwith_info()
show_whois_info()
get_item.counter = 0
traverse_communities(base_url, items)
