from collections import namedtuple

team_mapping = {
    'CHC': 'Cubs',
    'WSH': 'Nationals',
    'BAL': 'Orioles',
    'COL': 'Rockies',
    'KC': 'Royals',
    'TEX': 'Rangers',
    'MIN': 'Twins',
    'SEA': 'Mariners',
    'MIA': 'Marlins',
    'ARI': 'Diamondbacks',
    'CLE': 'Indians',
    'SF': 'Giants', 
    'TOR': 'Blue Jays',
    'OAK': 'Athletics', 
    'BOS': 'Red Sox', 
    'ATL': 'Braves', 
    'NYY': 'Yankees', 
    'TB': 'Rays', 
    'CIN': 'Reds', 
    'SD':'Padres',
    'LAA': 'Angels', 
    'STL': 'Cardinals', 
    'NYM': 'Mets', 
    'PIT': 'Pirates', 
    'MIL': 'Brewers', 
    'CWS': 'White Sox', 
    'PHI': 'Phillies', 
    'DET': 'Tigers', 
    'HOU': 'Astros', 
    'LAD': 'Dodgers'
}
inv_team_mapping = dict((v,k) for k,v in team_mapping.items())

def scrub_stringers(df):
    """Function to scrub out stringer data from data"""
    """https://tht.fangraphs.com/43416-2/"""
    ScrubSet = namedtuple('ScrubSet',"ev angle bb_type")
    to_scrub = []

    # pop-ups
    to_scrub.append(ScrubSet(ev=80,angle=69,bb_type="popup"))
    to_scrub.append(ScrubSet(ev=37,angle=62,bb_type="popup"))
    to_scrub.append(ScrubSet(ev=86,angle=67,bb_type="popup"))

    # Flyout
    to_scrub.append(ScrubSet(ev=71.4,angle=36.0,bb_type="fly_ball"))
    to_scrub.append(ScrubSet(ev=89,angle=39,bb_type="fly_ball"))
    to_scrub.append(ScrubSet(ev=89.2,angle=39.3,bb_type="fly_ball"))
    to_scrub.append(ScrubSet(ev=97,angle=30.2,bb_type="fly_ball"))

    # Line Drive
    to_scrub.append(ScrubSet(ev=90,angle=15,bb_type="line_drive"))
    to_scrub.append(ScrubSet(ev=90.4,angle=14.6,bb_type="line_drive"))
    to_scrub.append(ScrubSet(ev=91,angle=18,bb_type="line_drive"))
    to_scrub.append(ScrubSet(ev=91.1,angle=18.2,bb_type="line_drive"))
    to_scrub.append(ScrubSet(ev=98.8,angle=17.1,bb_type="line_drive"))

    # Ground balls
    to_scrub.append(ScrubSet(ev=40,angle=-36,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=40,angle=-36,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=40,angle=-36,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=40,angle=-36,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=41,angle=-39,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=43,angle=-62,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=84,angle=-20,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=83,angle=-21,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=82.9,angle=-20.7,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=90,angle=-17,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=90.2,angle=-13.0,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=90.3,angle=-17.3,bb_type="ground_ball"))
    to_scrub.append(ScrubSet(ev=84.0,angle=-13.0,bb_type="ground_ball"))


    df_return = df
    for streamer in to_scrub:
        bool_logic = (df_return["launch_speed"] == streamer.ev) & (df_return["launch_angle"] == streamer.angle) & (df_return["bb_type"] == streamer.bb_type)
        df_return = df_return.loc[~bool_logic]

    return df_return

