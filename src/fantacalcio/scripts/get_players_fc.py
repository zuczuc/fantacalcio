import pandas as pd
import requests
from bs4 import BeautifulSoup



INITIAL_PAGE = "https://www.fantacalcio.it/squadre/"
TEAMS = [
    "Atalanta",
    "Bologna",
    "Brescia",
    "Cagliari",
    "Fiorentina",
    "Genoa",
    "Inter",
    "Juventus",
    "Lazio",
    "lecce",
    "Milan",
    "Napoli",
    "Parma",
    "Roma",
    "Sampdoria",
    "Sassuolo",
    "Spal",
    "Torino",
    "Udinese",
    "Verona",
]



def remove_leading(txt, leading):
    while txt.startswith(leading):
        txt = txt[1:]
    return txt


def remove_trailing(txt, leading):
    while txt.endswith(leading):
        txt = txt[:-1]
    return txt


def clean_attributes(txt):
    txt = remove_leading(txt, ' ').replace(' cm', '').replace(' Kg', '')
    txt = txt.split("(")[0] # remove additional data like age in data di nascita
    txt = remove_trailing(txt, ' ')
    return txt


def get_links_for_team_fc(all_data, team):
    page = INITIAL_PAGE+str(team)
    data = requests.get(page).text
    soup = BeautifulSoup(data, "lxml")
    rosa = [div for div in soup.find_all('div') if div.get('id', None)=='rosa'][0]
    table = [table for table in rosa.find_all('table')][0]
    columns = [row.string for sec in table.find_all('thead') for row in sec.find_all('th')] + ['Link']
    players = [player for body in table.find_all('tbody') for player in body.find_all('tr')]
    players_data = [get_player_link_fc(player) for player in players]
    df_team = pd.DataFrame(columns=columns, data=players_data)
    if 'ID' in df_team.columns:
        df_team = df_team.drop('ID', axis=1)
    df_team['Squadra'] = team
    all_data = pd.concat((all_data, df_team))
    all_data.to_csv('player_links_fc.csv', index=False)
    return all_data


def get_player_link_fc(player):
    data = [d.string for d in player]
    link = player.find_all('a')[0].get('href')
    return data + [link]


def get_player_info_fc(link):
    page = "http:"+link
    data = requests.get(page).text
    soup = BeautifulSoup(data, "lxml")
    info_div = [div for div in soup.find_all('div') if div.get('id', None)=='info'][0]
    info_player = [li for li in info_div.find('ul').find_all('li')]
    titles = [ip.find('strong').text for ip in info_player]
    all_text = [ip.text for ip in info_player]
    raw_values = [txt.replace(ttl,'') for txt,ttl in zip(all_text,titles)]
    values = [clean_attributes(txt) for txt in raw_values]
    return pd.Series(index=titles, data=values)


def main():
#     all_data = pd.DataFrame()
#     for team in TEAMS:
#     #TODO: save data within main, not within get_links_for_team_fc
#         all_data = get_links_for_team_fc(all_data, team)
    all_data = pd.read_csv('player_links_fc.csv').set_index('CALCIATORE')
    links = all_data['Link']
    players = pd.DataFrame()
    for player_name,link in links.items():
        print("Getting data for player {}".format(player_name))
        info = pd.DataFrame({player_name: get_player_info_fc(link)}).T
        players = pd.concat((players, info))
    all_data = all_data.join(players, how='left')
    all_data.to_csv('player_data_fc.csv')
    print("Saved data to csv")
    

if __name__ == '__main__':
    main()