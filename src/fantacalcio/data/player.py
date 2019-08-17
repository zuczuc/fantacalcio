import seaborn as sns
import pandas as pd
import os

from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_GRADES_FN, FANTA_QUOTES_FN, FANTA_REMAP_FN, FANTA_ATTRS_FN
from fantacalcio.data.general import canceled_matches_grades_to_nan, remap_players


GRADES = canceled_matches_grades_to_nan(pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_GRADES_FN)))
REMAP_PLAYERS = pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_REMAP_FN)).set_index('Original')['Final'].to_dict()
GRADES = remap_players(GRADES, REMAP_PLAYERS)
ATTRIBUTES = pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_ATTRS_FN)).reset_index().set_index(['Player', 'Season'])


# QUOTATIONS

def find_matching_players(name, player_list):
    return [player for player in player_list if player.lower().startswith(name.lower())]


all_players = [str(p) for p in GRADES.reset_index()['Player'].unique().tolist()]
all_players.sort()
quotations = pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_QUOTES_FN)).\
    reset_index()[['Nome', 'R', 'Squadra', 'Qt. A', 'Qt. I']]
map_quotes_all = {long_name: find_matching_players(long_name, all_players) for \
    long_name in quotations['Nome'].values if find_matching_players(long_name, all_players)}
# Lazy; could create algo to get matching also for the missing names
map_quotes = {k: v[0] for k, v in map_quotes_all.items() if len(v)==1}
quotations['Nome'] = quotations['Nome'].map(lambda x:map_quotes.get(x, x))
QUOTATIONS = quotations.set_index('Nome')


class Player(object):
    '''Player object'''
    all_player_grades = GRADES.reset_index()
    all_player_quotes = QUOTATIONS
    all_player_attributes = ATTRIBUTES.reset_index()
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Player: {n}, {y}, {r} at {t}>'.format(n=self.name, y=int(self.player_age), r=self.role, t=self.current_team)
    
    @property
    def _data_player(self):
        name = self.name
        return self.all_player_grades.query("Player == '{n}'".format(n=name)).sort_values(['Season', 'Giornata'])

    @property
    def quotes(self):
        if self.name in self.all_player_quotes.index:
            return self.all_player_quotes.loc[self.name]

    @property
    def player_attributes(self):
        if self.name in self.all_player_attributes['Player'].values:
            return self.all_player_attributes.loc[self.all_player_attributes['Player']==self.name]

    @property
    def player_current_attributes(self):
        if self.player_attributes is None:
            return
        return self.player_attributes.set_index(['Season']).sort_index().iloc[-1]

    @property
    def player_date_of_birth(self):
        if self.player_current_attributes is None:
            return
        dob_str = self.player_current_attributes['Data_di_nascita'].split('/')
        dob = [int(s) for s in dob_str[::-1]]
        return pd.datetime(*dob).date()

    @property
    def player_age(self):
        if self.player_current_attributes is None:
            return
        return (pd.datetime.today().date() - self.player_date_of_birth).days / 365.25

    @property
    def player_nation(self):
        if self.player_current_attributes is None:
            return
        return self.player_current_attributes['Nazionalita']

    @property
    def player_height(self):
        if self.player_current_attributes is None:
            return
        return self.player_current_attributes['Altezza']

    @property
    def player_weight(self):
        if self.player_current_attributes is None:
            return
        return self.player_current_attributes['Peso']

    @property
    def teams(self):
        return self._data_player.Team.unique().tolist()

    @property
    def current_team(self):
        if self.quotes is not None:
            return self.quotes['Squadra']
        else:
            return self.teams[-1]

    @property
    def role(self):
        if self.quotes is not None:
            return self.quotes['R']
        else:
            return self._data_player.Role.unique().tolist()[0]
    
    @property
    def all_stats(self):
        return self._data_player.set_index(['Season', 'Giornata'])[['Voto', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FantaVoto']]

    @property
    def grades(self):
        return self.all_stats['Voto']

    @property
    def fantagrades(self):
        return self.all_stats['FantaVoto']

    @property
    def all_grades(self):
        return self.all_stats[['Voto', 'FantaVoto']]
    
    def plot(self, attributes, *args, **kwargs):
        title = self.__repr__()[1:-1]
        lines = self.all_stats[attributes]
        return lines.plot(title=title, kind='bar', *args, **kwargs)

    def subplot(self, attributes, *args, **kwargs):
        title = self.__repr__()[1:-1]
        lines = self.all_stats[attributes]
        seasons = lines.reset_index().Season.unique().tolist()
        # subplot = sns.plt.subplots(len(seasons), 1)
        for season in seasons:
            lines.loc[season].plot(kind='bar', title=title+', Season {}'.format(int(season)), *args, **kwargs)
