import os
import shutil
import csv
import requests
import time
from bs4 import BeautifulSoup

url = 'https://www.footballdatabase.eu'


cookies = {
    'trc_cookie_storage': 'taboola%2520global%253Auser-id%3D7966384e-086d-4bbe-a0ca-2d81259d2bc0-tucta22ed2a',
    'PHPSESSID': 'pk93096s7qsqh6oob1o8lauo7u',
    'fbdb_auth': '23f5e3f154aa0542d249d820c92fff79',
    '_pbjs_userid_consent_data': '6683316680106290',
    '_ga_31VFXW2CM3': 'GS1.1.1668163872.19.1.1668164505.0.0.0',
    '_ga': 'GA1.2.789686284.1667945622',
    '_gid': 'GA1.2.293859119.1668164506',
    '_gat_gtag_UA_1896429_1': '1',
    'cto_bidid': 'zTi4NF8xRTh1eFcxRmpWVWl6cVJOQlhTczBtUndyQnZhV0xXbTVRQ2wlMkZyaFFmTjZRRG5yQnklMkYzMUdmak40MFVFVzY5QmlBdnVXWENzSlBwQWdCTWJiNFVzTUV3QUFXYk9hamxxRFRKNGNNWFpMOExDVVY3YW1rUHpLQkNKTVdCNUxNcjQ',
    'nadz_dailyVisits': '1',
    'cto_bundle': 'VfxNHl9QNWVNWXRvbWZBUHczZjZVOUh5ME90QVg4T28xMU51TzJwRDhJUFpydHlicmE1eVd5c1lnNlNPWE1DTmNVJTJGd25aU240dVNwTThjeGg2cmtOWW5iZG12a0pMNEdSVTlwd0JuQ3pkaVI0bmFTS0FtS1JrY1NZVWYlMkY1ZGh1RVpqMEJNUnJJM29xQXY1M2laRVRmQWYlMkZiTnJGRWlyUXlkQVgxOTIlMkJ3MnlrM1BKTSUzRA',
}

headers = {
    'authority': 'www.footballdatabase.eu',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'trc_cookie_storage=taboola%2520global%253Auser-id%3D7966384e-086d-4bbe-a0ca-2d81259d2bc0-tucta22ed2a; PHPSESSID=pk93096s7qsqh6oob1o8lauo7u; fbdb_auth=23f5e3f154aa0542d249d820c92fff79; _pbjs_userid_consent_data=6683316680106290; _ga_31VFXW2CM3=GS1.1.1668163872.19.1.1668164505.0.0.0; _ga=GA1.2.789686284.1667945622; _gid=GA1.2.293859119.1668164506; _gat_gtag_UA_1896429_1=1; cto_bidid=zTi4NF8xRTh1eFcxRmpWVWl6cVJOQlhTczBtUndyQnZhV0xXbTVRQ2wlMkZyaFFmTjZRRG5yQnklMkYzMUdmak40MFVFVzY5QmlBdnVXWENzSlBwQWdCTWJiNFVzTUV3QUFXYk9hamxxRFRKNGNNWFpMOExDVVY3YW1rUHpLQkNKTVdCNUxNcjQ; nadz_dailyVisits=1; cto_bundle=VfxNHl9QNWVNWXRvbWZBUHczZjZVOUh5ME90QVg4T28xMU51TzJwRDhJUFpydHlicmE1eVd5c1lnNlNPWE1DTmNVJTJGd25aU240dVNwTThjeGg2cmtOWW5iZG12a0pMNEdSVTlwd0JuQ3pkaVI0bmFTS0FtS1JrY1NZVWYlMkY1ZGh1RVpqMEJNUnJJM29xQXY1M2laRVRmQWYlMkZiTnJGRWlyUXlkQVgxOTIlMkJ3MnlrM1BKTSUzRA',
    'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
}

csv_players_columns = ['name', 'club', 'age', 'nationality', 'caps',
                       'height', 'weight', 'first cap', 'best foot', 'photo']

try:
    csv_file = open('football.csv', 'w')

    csv_writer = csv.DictWriter(csv_file, fieldnames=csv_players_columns)
    csv_writer.writeheader()

    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('An error occurs while trying to access the website')

    soup = BeautifulSoup(response.content, 'html.parser')

    top_clubs = soup.find_all(name='div', attrs={'class': 'topclubs'})

    clubs_anchors = []

    for top_clubs_section in top_clubs:
        anchor = top_clubs_section.find_all(name='a')
        clubs_anchors.extend(anchor)

    players_links = []

    for anchor in clubs_anchors:
        club_data = requests.get('{url}{href}'.format(
            url=url, href=anchor.get('href')), headers=headers, cookies=cookies)

        club_cards = BeautifulSoup(
            club_data.content, 'html.parser').find_all('div', {'class': 'card-player'})

        for card in club_cards:
            player_anchor = card.find('a')
            if player_anchor:
                players_links.append(player_anchor.get('href'))

    for href in players_links:
        player_page = requests.get('{url}{href}'.format(
            url=url, href=href), headers=headers, cookies=cookies)

        soup_player_data = BeautifulSoup(player_page.content, 'html.parser').find(
            'div', {'class': 'player_technical'})

        player_name = soup_player_data.find(
            'div', {'class', 'titlePlayer'}).find('h1').text

        player_club = soup_player_data.find(
            'div', {'class', 'club'}).find('a').text

        first_line_data = soup_player_data.find('div', {'class', 'infoPlayer'}).find(
            'div', {'class', 'line'}).find_all('div', {'class', 'data'})

        second_line_data = soup_player_data.find('div', {'class', 'infoPlayer'}).find(
            'div', {'class', 'linesecond'}).find_all('div', {'class', 'data'})

        player_age = None
        player_nationality = None
        player_height = None
        player_weight = None
        player_best_foot = None

        if len(first_line_data) == 0:
            player_age = None
            player_nationality = None
            player_height = None
            player_weight = None
            player_best_foot = None

        if len(first_line_data) >= 1 and first_line_data[0].text:
            player_age = first_line_data[0].find(attrs={'class', 'age'}).text
            player_nationality = first_line_data[0].find(
                attrs={'class', 'secondline'}).find('a').text

        if len(first_line_data) >= 2 and first_line_data[1].text:
            player_height = first_line_data[1].find(
                attrs={'class', 'firstline'}).text.split(':')[1] if first_line_data[1].find(
                attrs={'class', 'firstline'}) else None
            player_weight = first_line_data[1].find(
                attrs={'class', 'secondline'}).text.split(':')[1] if first_line_data[1].find(
                attrs={'class', 'secondline'}) else None

        player_best_foot = first_line_data[2].text.split(':')[1] if len(
            first_line_data) >= 3 else None

        player_caps = None
        player_first_cap = None
        if len(second_line_data) == 0:
            player_caps = None
            player_first_cap = None

        player_caps = second_line_data[0].find('a').text if len(
            second_line_data) >= 1 and second_line_data[0].find('a') else None

        player_first_cap = second_line_data[1].find('a').text if len(
            second_line_data) >= 2 and second_line_data[1].find('a') else None

        player_photo_src = soup_player_data.find(
            attrs={'class', "subphoto"}).find('img').get('src') if soup_player_data.find(
            attrs={'class', "subphoto"}) else None

        player_all_data = {
            'name': player_name,
            'club': player_club,
            'age': player_age,
            'nationality': player_nationality,
            'caps': player_caps,
            'height': player_height,
            'weight': player_weight,
            'first cap': player_first_cap,
            'best foot': player_best_foot,
            'photo': '{}{}'.format(url, player_photo_src)
        }

        csv_writer.writerow(player_all_data)


finally:
    csv_file.close()
