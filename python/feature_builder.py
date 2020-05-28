from helper_functions import inv_team_mapping
from pybaseball import league_batting_stats

from bs4 import BeautifulSoup
import requests

import numpy as np
import pandas as pd

def add_spray_angle(df):
    df["spray_angle"] = np.arctan((df["hc_x"]-125.42)/(198.27-df["hc_y"]))*180/np.pi*.75
    df["adj_spray_angle"] = df .apply(lambda row: -row["spray_angle"] if row["stand"] == "L" else row["spray_angle"], axis=1)
    return df

def add_sprint_speed(df, year):
    sprint_speeds = pd.read_csv("../data/{0}_sprint_speed.csv".format(year))
    sprint_speeds = sprint_speeds[["player_id","sprint_speed"]]
    return_df = df.merge(sprint_speeds, how="left", left_on="batter", right_on="player_id")
    return_df["sprint_speed"] = return_df["sprint_speed"].fillna(return_df["sprint_speed"].mean())
    return return_df
                                

def add_stealing_parameters(df, start, end):
    batting_stats=league_batting_stats.batting_stats_range(start,end)

    # Get SB Values
    sb_figures = batting_stats[["Name","SB","CS"]]
    sb_figures["Name"] = sb_figures['Name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    sb_figures["attempted_sb"] = sb_figures["SB"].astype(int) + sb_figures["CS"].astype(int)
    sb_figures["sb_rate"] = sb_figures["SB"].astype(int) / ( sb_figures["SB"].astype(int) + sb_figures["CS"].astype(int))
    sb_figures["sb_rate"] = sb_figures["sb_rate"].fillna(-99)

    # GET PLAYER IDS
    playerid = pd.read_csv("../data/playeridmap.csv")
    idframe = playerid[["PLAYERNAME","MLBID"]]
    sb_figures = sb_figures.merge(idframe, how="left", left_on="Name", right_on="PLAYERNAME")

    # Merge
    return_df = df.merge(sb_figures, how='left', left_on="batter", right_on="MLBID")

    for placeholder in ["MLBID", "PLAYERNAME"]:
        return_df = return_df.drop(placeholder, axis=1)

    return return_df



def add_park_factors(df,year):

    # Scrape the Data to pf_df 
    pf_page = 'https://www.fangraphs.com/guts.aspx?type=pfh&teamid=0&season={0}'.format(year)
    page = requests.get(pf_page)
    soup = BeautifulSoup(page.text, 'html.parser')
    found = soup.find('table',{'class':'rgMasterTable', 'id':'GutsBoard1_dg1_ctl00'})
    pf_df=pd.read_html(str(found))[0]

    # Map pf_df to sensible names to add
    mapper = {
    "1B as L" :"1b_pf_l",
    "2B as L" :"2b_pf_l",
    "3B as L" :"3b_pf_l",
    "HR as L" :"hr_pf_l",
    "1B as R" :"1b_pf_r",
    "2B as R" :"2b_pf_r",
    "3B as R" :"3b_pf_r",
    "HR as R" :"hr_pf_r",
    }

    park_factors_keep_df = pf_df[list(mapper.keys())+["Team"]]
    park_factors_keep_df["park"] = park_factors_keep_df["Team"].map(inv_team_mapping)
    park_factors = park_factors_keep_df.rename(mapper=mapper, axis=1)

    df = df.merge(park_factors, how='left', left_on="home_team", right_on="park")
    df["1b_park_factor"] = df.apply(lambda row: row["1b_pf_l"] if row["stand"] == "L" else row["1b_pf_r"], axis=1)
    df["2b_park_factor"] = df.apply(lambda row: row["2b_pf_l"] if row["stand"] == "L" else row["2b_pf_r"], axis=1)
    df["3b_park_factor"] = df.apply(lambda row: row["3b_pf_l"] if row["stand"] == "L" else row["3b_pf_r"], axis=1)
    df["hr_park_factor"] = df.apply(lambda row: row["hr_pf_l"] if row["stand"] == "L" else row["hr_pf_r"], axis=1)

    for placeholder in mapper.values():
        df = df.drop(placeholder, axis=1)

    df = df.drop("Team",axis=1)
    df = df.drop("park",axis=1)
    return df

