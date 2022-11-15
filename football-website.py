import csv
import time

import requests
from bs4 import BeautifulSoup

url = 'https://www.footballdatabase.eu'


cookies = {
    'nadz_dailyVisits': '1',
    '_gid': 'GA1.2.1107512693.1668538883',
    '_gat_gtag_UA_1896429_1': '1',
    'PHPSESSID': 'csqha4bfi2m57o43bvilhpmci3',
    'fbdb_auth': 'ea8297af40254576a2429b88aeba824f',
    '_ga_31VFXW2CM3': 'GS1.1.1668540897.2.1.1668544213.0.0.0',
    '_ga': 'GA1.2.1856903666.1668538881',
}

headers = {
    'authority': 'www.footballdatabase.eu',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'nadz_dailyVisits=1; _gid=GA1.2.1107512693.1668538883; _gat_gtag_UA_1896429_1=1; PHPSESSID=csqha4bfi2m57o43bvilhpmci3; fbdb_auth=ea8297af40254576a2429b88aeba824f; _ga_31VFXW2CM3=GS1.1.1668540897.2.1.1668544213.0.0.0; _ga=GA1.2.1856903666.1668538881',
    'origin': 'https://www.footballdatabase.eu',
    'referer': 'https://www.footballdatabase.eu/en/player/details/10973-lionel-messi',
    'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42',
}

csv_players_columns = ['name', 'club', 'age', 'nationality', 'caps',
                       'height', 'weight', 'first cap', 'best foot', 'photo', 'positions', 'clean sheets', "clean sheets", "goals conceded",  "minutes played",  "played matched",  "impacting goals",  "goals",  "impacting assists",  "assists",  "yellow cards", "red cards", "identities"]

try:
    csv_file = open('football.csv', 'w', encoding="utf-8")

    csv_writer = csv.DictWriter(csv_file, fieldnames=csv_players_columns)
    csv_writer.writeheader()

    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('An error occurs while trying to access the website')

    soup = BeautifulSoup(response.content, 'html.parser')

    print(f"Successfully connected with {url}.")

    top_clubs = soup.find_all(name='div', attrs={'class': 'topclubs'})
    if not top_clubs:
        raise Exception(
            "Error while scraping the website, Top Clubs are missed. check your Authentication.")

    clubs_anchors = []

    for top_clubs_section in top_clubs:
        anchors = top_clubs_section.find_all(name='a')
        clubs_anchors.extend(anchors)

    if len(clubs_anchors) > 10:
        raise Exception("Can't get all top 10 clubs from the website.")

    players_links = []

    i = 1
    for anchor in clubs_anchors:
        club_data = requests.get('{url}{href}'.format(
            url=url, href=anchor.get('href')), headers=headers, cookies=cookies)

        club_cards = BeautifulSoup(
            club_data.content, 'html.parser').find_all('div', {'class': 'card-player'})
        print(f'Getting club {i} data...')

        for card in club_cards:
            player_anchor = card.find('a')
            if player_anchor:
                players_links.append(player_anchor.get('href'))
        if i == 1:
            break
        i += 1

    print(f'Number of players in top 10 clubs is: {len(players_links)}.')

    j = 1
    for href in players_links:
        if j > 1:
            print('✔')

        player_page = requests.get('{url}{href}'.format(
            url=url, href=href), headers=headers, cookies=cookies)

        soup_player_page = BeautifulSoup(player_page.content, 'html.parser')
        print(f'Getting player {j} data...')

        player_information = soup_player_page.find(
            'div', {'class': 'player_technical'})
        if player_information is None:
            raise Exception(
                "Can't get the data for another players because requests limitation.")

        player_name = player_information.find(
            'div', {'class', 'titlePlayer'}).find('h1').text if player_information else None

        player_club = player_information.find(
            'div', {'class', 'club'}).find('a').text if player_information else None

        first_line_data = player_information.find('div', {'class', 'infoPlayer'}).find(
            'div', {'class', 'line'}).find_all('div', {'class', 'data'})

        second_line_data = player_information.find('div', {'class', 'infoPlayer'}).find(
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

        player_photo_src = player_information.find(
            attrs={'class', "subphoto"}).find('img').get('src') if player_information.find(
            attrs={'class', "subphoto"}) else None

        current_season_statistics_section = soup_player_page.find(
            attrs={'class': 'currentseasonstats'})

        if current_season_statistics_section:
            try:
                player_clean_sheets = current_season_statistics_section.find(
                    attrs={'class': "s_cleansheets"}).findChildren()[0].text
            except AttributeError:
                player_clean_sheets = None

            try:
                player_goals_conceded = current_season_statistics_section.find(
                    attrs={'class': "s_cleansheets"}).findChildren()[2].text
            except AttributeError:
                player_goals_conceded = None

            try:
                player_minutes_played = current_season_statistics_section.find(
                    attrs={'class': "s_played_matches"}).findChildren()[0].text
            except AttributeError:
                player_minutes_played = None

            try:
                player_played_matched = current_season_statistics_section.find(
                    attrs={'class': "s_played_matches"}).findChildren()[2].text
            except AttributeError:
                player_played_matched = None

            try:
                player_impacting_goals = current_season_statistics_section.find(
                    attrs={'class': "s_impactgoals"}).findChildren()[0].text
            except AttributeError:
                player_impacting_goals = None

            try:
                player_goals = current_season_statistics_section.find(
                    attrs={'class': "s_impactgoals"}).findChildren()[2].text
            except AttributeError:
                player_goals = None

            try:
                player_impacting_assists = current_season_statistics_section.find(
                    attrs={'class': "s_impactassists"}).findChildren()[0].text
            except AttributeError:
                player_impacting_assists = None

            try:
                player_assists = current_season_statistics_section.find(
                    attrs={'class': "s_impactassists"}).findChildren()[2].text
            except AttributeError:
                player_assists = None

            try:
                player_yellow_cards = current_season_statistics_section.find(
                    attrs={'class': "s_yellowcards"}).findChildren()[0].text
            except AttributeError:
                player_yellow_cards = None

            try:
                player_red_cards = current_season_statistics_section.find(
                    attrs={'class': "s_yellowcards"}).findChildren()[2].text
            except AttributeError:
                player_red_cards = None

        player_position_section = soup_player_page.find(
            attrs={'class': 'playerposition'})

        if player_position_section:
            try:
                player_main_position = {
                    "name": player_position_section.find(attrs={'class': 'mainposition'}).findChildren()[0].text,
                    'percentage': player_position_section.find(attrs={'class': 'mainposition'}).findChildren()[1].text
                }
            except AttributeError:
                player_main_position = None

            try:
                player_other_positions = []

                for position in player_position_section.find_all(attrs={'class': 'otherpositions'}):
                    player_other_positions.append({
                        'name': position.findChildren()[0].text,
                        'percentage': position.findChildren()[1].text
                    })
                if not len(player_other_positions):
                    player_other_positions = None

            except:
                player_other_positions = None
        try:
            player_identities = list(map(lambda identity: identity.text, soup_player_page.find_all_next(
                attrs={'class': 'nameIdentity'})))

        except AttributeError:
            player_identities = None

        player_career_statistics_section = soup_player_page.find(
            attrs={'class': 'player_career'})

        if player_career_statistics_section:
            statistics_lines = player_career_statistics_section.table.find_all(
                'tr', recursive=False, attrs={'class': 'line'})
            for line in statistics_lines[2:-1]:

                season = line.find(attrs={"class": "season"})
                club = line.find(attrs={"class": "club"})
                tire = line.find(attrs={"class": "champ"})
                matchs_played = line.find(attrs={"class": "matchsplayed"})

                player_statistic = '{} {}'.format(season, club): {
                        "tire": tire,
                        "matchs played": matchs_played
                    }
                

        player_information = {
            'name': player_name,
            'club': player_club,
            'age': player_age,
            'nationality': player_nationality,
            'caps': player_caps,
            'height': player_height,
            'weight': player_weight,
            'first cap': player_first_cap,
            'best foot': player_best_foot,
            'photo': '{}{}'.format(url, player_photo_src),
            "positions": {
                "main position": player_main_position,
                "other positions": player_other_positions
            },
            "clean sheets": player_clean_sheets,
            "goals conceded": player_goals_conceded,
            "minutes played": player_minutes_played,
            "played matched": player_played_matched,
            "impacting goals": player_impacting_goals,
            "goals": player_goals,
            "impacting assists": player_impacting_assists,
            "assists": player_assists,
            "yellow cards": player_yellow_cards,
            "red cards": player_red_cards,
            "identities": player_identities,
            # "player career statistics data": {
            #     'offense': ,
            #     'defense': ,
            #     'playing time': ,
            #     'discipline': ,
            #     'results': ,

            # }

        }
        csv_writer.writerow(player_information)
        j += 1
        break

    print('Players data was added to football.csv file successfully.')

finally:
    csv_file.close()
