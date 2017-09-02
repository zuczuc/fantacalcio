import pandas as pd

def canceled_matches_grades_to_nan(grades):
    n_players = grades.groupby(["Season", "Giornata", "Team"]).count()["Player"]
    canceled_matches = n_players.loc[n_players>15]
    
    del_index = []
    for s, g, t in canceled_matches.index:
        del_index += grades.query("Season == {s}".format(s=s)).query("Giornata == {g}".format(g=g)).query("Team == '{t}'".format(t=t)).index.tolist()
    
    grades.set_value(index=del_index, col=["V", "G", "A", "R", "R", "AG", "AM", "ES", "FV"], value=pd.np.NaN)
    grades[grades.index.isin(del_index)].head()
    
    return grades.rename(columns={'FV':'FantaVoto', 'V':'Voto'})