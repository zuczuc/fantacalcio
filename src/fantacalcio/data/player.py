import os
import getpass
import pandas as pd

from fantacalcio.config_data.config_data import FOLDER_FANTA_INPUT, FANTA_GRADES_FN
from fantacalcio.data.general import canceled_matches_grades_to_nan


GRADES = canceled_matches_grades_to_nan(pd.read_csv(os.path.join(FOLDER_FANTA_INPUT, FANTA_GRADES_FN)))
OUTPUT_FOLDER = FOLDER_FANTA_INPUT[getpass.getuser()]


class Player(object):
    ''' Player object'''
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Player: {n}: {r} at {t}>'.format(n=self.name, r=self.role, t=self.teams[-1])
    
    @property
    def _data_player(self):
        name = self.name
        return GRADES.query('Player == {n}'.format(n=name))
    
    @property
    def teams(self):
        return self._data_player.Team.unique().tolist()
    
    @property
    def role(self):
        return self._data_player.Role.unique().tolist()[0]
    
    @property
    def _grades(self):
        return self._data_player.set_index(['Season', 'Giornata'])[['Voto', 'G', 'A', 'R', 'RS', 'AG', 'AM', 'ES', 'FantaVoto']]

    @property
    def grades(self):
        return self._grades['Voto']

    @property
    def fantagrades(self):
        return self._grades['FantaVoto']

    @property
    def all_grades(self):
        return self._grades[['Voto', 'FantaVoto']]
    
    def plot(self, propert, *args, **kwargs):
        title = self.__repr__()[1:-1]
        lines = getattr(self, propert)
        return lines.plot(title=title, *args, **kwargs)