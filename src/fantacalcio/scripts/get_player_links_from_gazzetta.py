import os
import getpass
import pandas as pd
import requests
from bs4 import BeautifulSoup

from scraping import get_team_soups, get_player_soup, get_player_name, get_player_link, get_attribute_from_player_soup
from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_LINKS_FN, FANTA_ATTRS_FN


PAGES_GRADES = {'2014':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2014-15/giornata-",
                '2015':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2015-16/giornata-",
                '2016':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2016-17/giornata-",}
N_GIORNATE = 38
INDICES=['V', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FV']
OUTPUT_FOLDER = FOLDER_FANTA_INPUT[getpass.getuser()]



def get_player_links_from_gazzetta():
    # Get links in a dictionary
    all_links = dict()
    for season,page_grades in PAGES_GRADES.items():
        for giornata in range(1,N_GIORNATE+1):
            for team_soup in get_team_soups(page_grades, giornata):
                _, player_soups = get_player_soup(team_soup)
                for player_soup in player_soups:
                    all_links[(get_player_name(player_soup), season)] = get_player_link(player_soup)
    # Move links to a DF
    all_links_df = pd.DataFrame(columns=['Player', 'Season', 'Link'])
    for k,v in all_links.items():
        all_links_df = all_links_df.append(pd.DataFrame(data=[[k[0], k[1], v]], columns=['Player', 'Season', 'Link']))
    all_links_df = all_links_df.set_index(['Season', 'Player']).sort_index().reset_index()
    return all_links_df

def get_player_attributes_from_links(all_links_df):
    columns = ['Player', 'Season', 'Link', 'Ruolo', 'Squadra', 'Data_di_nascita', 'Nazionalita', 'Altezza', 'Peso']
    player_attributes = pd.DataFrame(columns=columns)
    for row in all_links_df.index:
        player_name = all_links_df.loc[row]['Player']
        player_season = all_links_df.loc[row]['Season']
        player_link = all_links_df.loc[row]['Link']
        player_soup = BeautifulSoup(requests.get(player_link).text, "lxml")
        try:
            player_data = get_attribute_from_player_soup(player_soup)
        except IndexError:
            print('ERROR in downloading attributes: player {}, season {}, link {}'.format(player_name, player_season, player_link))
            continue
        player_data['Player'] = player_name
        player_data['Season'] = player_season
        player_data['Link'] = player_link
        player_attributes = player_attributes.append(player_data)
    return player_attributes[columns]

def main():
    all_links_df = get_player_links_from_gazzetta()
    all_links_df.to_csv(os.path.join(OUTPUT_FOLDER, FANTA_LINKS_FN), index=False)
#     all_links_df = pd.read_csv(os.path.join(OUTPUT_FOLDER, FANTA_LINKS_FN))
    player_attributes = get_player_attributes_from_links(all_links_df)
    player_attributes.to_csv(os.path.join(OUTPUT_FOLDER, FANTA_ATTRS_FN), index=False)

if __name__ == '__main__':
    main()