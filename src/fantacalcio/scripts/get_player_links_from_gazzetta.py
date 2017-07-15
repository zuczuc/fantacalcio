import os
import getpass
import pandas as pd

from scraping import get_team_soups, get_player_soup, get_player_name, get_player_link
from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_LINKS_FN


PAGES_GRADES = {'2014':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2014-15/giornata-",
                '2015':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2015-16/giornata-",
                '2016':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2016-17/giornata-",}
N_GIORNATE = 38
INDICES=['V', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FV']
OUTPUT_FOLDER = FOLDER_FANTA_INPUT[getpass.getuser()]



def main():
    all_links = pd.DataFrame(columns=['Player', 'Season', 'Link'])
    for season,page_grades in PAGES_GRADES.items():
        for giornata in range(1,N_GIORNATE+1):
            for team_soup in get_team_soups(page_grades, giornata):
                team, player_soups = get_player_soup(team_soup)
                for player_soup in player_soups:
                    all_links = all_links.append(pd.DataFrame(
                            data=[[get_player_name(player_soup), season, get_player_link(player_soup)]],
                            columns=['Player', 'Season', 'Link']))
    
    all_links_df = pd.DataFrame(columns=['Player', 'Season', 'Link'])
    for k,v in all_links.items():
        all_links_df = all_links_df.append(pd.DataFrame(data=[[k[0], k[1], v]], columns=['Player', 'Season', 'Link']))
    
    all_links_df.to_csv(os.path.join(OUTPUT_FOLDER, FANTA_LINKS_FN), index=False)



if __name__ == '__main__':
    main()