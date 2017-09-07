import os
import pandas as pd
from logging import Logger

from scraping import get_team_soups, get_player_soup, get_player_stats
from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_GRADES_FN

log = Logger('get_grades_from_gazzetta')
log.setLevel('INFO')


# INPUTS

# page_votes = "https://www.fantagazzetta.com/voti-serie-a/2016-17/"
PAGES_GRADES = {'2014':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2014-15/giornata-",
                '2015':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2015-16/giornata-",
                '2016':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2016-17/giornata-",
                '2017':"http://www.gazzetta.it/calcio/fantanews/voti/serie-a-2017-18/giornata-",
}

N_GIORNATE = {'2014':38,
            '2015':38,
            '2016':38,
            '2017':2,
}

INDICES=['V', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FV']
OUTPUT_FOLDER = FOLDER_FANTA_INPUT[os.environ['USERNAME']]



# FUNCTIONS

def main():
    all_stats = pd.DataFrame()
    for season,page_grades in PAGES_GRADES.items():
        print("\n"+"-"*160)
        print("Loading season {s1}-{s2}".format(s1=season,s2=str(int(season)+1)))
        season_stats = pd.DataFrame()
        for giornata in range(1,N_GIORNATE[season]+1):
            print("Season {}, giornata {}".format(str(season), str(giornata)))
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
    log.info("Writing to csv")
    all_stats.to_csv(os.path.join(OUTPUT_FOLDER, FANTA_GRADES_FN))
log.info("Finished script!")

if __name__ == '__main__':
    main()