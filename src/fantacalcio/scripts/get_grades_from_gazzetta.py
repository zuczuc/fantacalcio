import os
import getpass
import pandas as pd

from scraping import get_team_soups, get_player_soup, get_player_stats
from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_GRADES_FN


# INPUTS

# page_votes = "https://www.fantagazzetta.com/voti-serie-a/2016-17/"
PAGES_GRADES = {'2014':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2014-15/giornata-",
                '2015':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2015-16/giornata-",
                '2016':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2016-17/giornata-",}
N_GIORNATE = 38
INDICES=['V', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FV']
OUTPUT_FOLDER = FOLDER_FANTA_INPUT[getpass.getuser()]



# FUNCTIONS

def main():
    all_stats = pd.DataFrame()
    for season,page_grades in PAGES_GRADES.items():
        season_stats = pd.DataFrame()
        for giornata in range(1,N_GIORNATE+1):
            team_stats = pd.DataFrame()
            for team_soup in get_team_soups(page_grades, giornata):
                team, player_soups = get_player_soup(team_soup)
                player_stats = pd.DataFrame()
                for player_soup in player_soups:
                    player_name, role, stats = get_player_stats(player_soup, indices=INDICES)
                    ps = pd.DataFrame({player_name:stats}).T
                    ps['Role'] = role
                    player_stats = pd.concat([player_stats, ps])
                player_stats = player_stats.reset_index().rename(columns={'index':'Player'})
                player_stats['Team'] = team
                team_stats = pd.concat([team_stats, player_stats])
            team_stats['Giornata'] = str(giornata)
            season_stats = pd.concat([season_stats, team_stats])
        season_stats['Season'] = season
        all_stats = pd.concat([all_stats, season_stats])
    all_stats = all_stats.set_index(['Season', 'Giornata', 'Team', 'Player'])
    all_stats.to_csv(os.path.join(OUTPUT_FOLDER, FANTA_GRADES_FN))

if __name__ == '__main__':
    main()