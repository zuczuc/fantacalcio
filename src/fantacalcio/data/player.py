import os
import pandas as pd

from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_GRADES_FN, FANTA_REMAP_FN
from fantacalcio.data.general import canceled_matches_grades_to_nan, remap_players


GRADES = canceled_matches_grades_to_nan(pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_GRADES_FN)))
REMAP_PLAYERS = pd.read_csv(os.path.join(FOLDER_FANTA_INPUT[os.environ['USERNAME']], FANTA_REMAP_FN)).set_index('Original')['Final'].to_dict()
GRADES = remap_players(GRADES, REMAP_PLAYERS)


class Player(object):
    ''' Player object'''
    all_player_grades = GRADES.reset_index()
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Player: {n}: {r} at {t}>'.format(n=self.name, r=self.role, t=self.teams[-1])
    
    @property
    def _data_player(self):
        name = self.name
        return self.all_player_grades.query("Player == '{n}'".format(n=name)).sort_values(['Season', 'Giornata'])
    
    @property
    def teams(self):
        return self._data_player.Team.unique().tolist()
    
    @property
    def role(self):
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
        return lines.plot(title=title, *args, **kwargs)