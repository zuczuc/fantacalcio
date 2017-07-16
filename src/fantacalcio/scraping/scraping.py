import pandas as pd
import requests
from bs4 import BeautifulSoup


INDICES=['V', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FV']

def clean_table_cells(st):
    st = st.replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', '')
    try:
        return float(st)
    except ValueError:
        return pd.np.NaN

def get_team_soups(page_votes, giornata):
    # Get html data from page+giornata
    page = page_votes+str(giornata)
    r = requests.get(page)
    data = r.text
    # Navigate inside data using BS
    soup = BeautifulSoup(data, "lxml")
    soup1 = [sec for sec in soup.html.body.find_all('section') if sec.get('class', None)==['main-container']][0]
    soup2 = [sec for sec in soup1.find_all('section') if sec.get('class', None)==['section-standard-row']][0]
    soup3 = [sec for sec in soup2.find_all('div') if sec.get('class', None)==["MXXX-central-articles-main-column"]][0]
    soup4 = [sec for sec in soup3.find_all('div') if
                   sec.get('class', None)==['magicDayList', 'listView', 'magicDayListChkDay']][0]
    return [sec for sec in soup4.find_all('div') if sec.get('class', None)==['singleRound']]

def get_player_soup(team_soup):
    team_list = [sec for sec in team_soup.find_all('div') if sec.get('class', None)==["magicTeamListContainer"]][0]
    team_grades = [sec for sec in team_list.find_all('ul') if sec.get('class')==["magicTeamList"]][0]
    team = [span.contents[0] for span in team_grades.li.div.find_all('span') if span.get('class', None)==["teamNameIn"]][0]
    player_soups = team_grades.find_all('li')[1:]
    return team, player_soups

def get_player_name(player_soup):
    return [span.string for span in player_soup.div.div.find_all('span') if span.get('class',None)==["playerNameIn"]][0]

def get_player_link(player_soup):
    return [a.get('href') for a in player_soup.find_all('a') if a.get('href', None)!=None][0]

def get_player_stats(player_soup, indices=INDICES):
    player_name = get_player_name(player_soup)
    role = [span.string for span in player_soup.div.find_all('span') if
            span.get('class',None)==["playerRole", "show-for-small"]][0]
    stats = pd.Series(data=[clean_table_cells(div.string)
            for div in player_soup.find_all('div') if div.get('class', None)[0] == "inParameter"],
      index=indices)
    player_in = [sp for sp in player_soup.find_all('span') if sp.get('class',None)==['playerStats', 'icon', 'down']]
    player_out = [sp for sp in player_soup.find_all('span') if sp.get('class',None)==['playerStats', 'icon', 'up']]
    pi = 1 if len(player_in)>0 else 0
    po = 1 if len(player_out)>0 else 0
    stats = stats.append(pd.Series(index=['In', 'Out'], data = [pi, po]))
    return player_name, role, stats

def get_attribute_from_text(str):
    return clean_attributes(str.replace('\r', '').replace('\n', '').replace('\t', '').replace('  ', '').replace(' ', '_')).\
         split(':')

def clean_attributes(str):
    return str.replace('_cm', '').replace('_kg', '')

def get_attribute_from_player_soup(player_soup):
    # Navigate towards the place where information is stored
    main_container = [sec for sec in player_soup.body.find_all('section') if sec.get('class',None)==['main-container']][0]
    opener = [sec for sec in main_container.find_all('section') if sec.get('class',None)==['opener']][0]
    opener2 = [div for div in opener.find_all('div') if div.get('class',None)==['MXXX-section-opener-column']][0]
    opener3 = [sec for sec in opener2.find_all('section') if sec.get('class',None)==['profilo-giocatore']][0]
    profile = [div for div in opener3.find_all('div') if div.get('class',None)==["first_half_profilo"]][0]
    profile_data = [div for div in profile.find_all('div') if div.get('class',None)==["right"]][0]
    # Get the data and store it in a df
    data=[get_attribute_from_text(p.get_text()) for p in profile_data.find_all('p')]
    return pd.DataFrame(data=[[d[1] for d in data]], columns=[d[0] for d in data])