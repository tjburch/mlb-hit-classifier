# Classes to construct and evaluate wOBA
# tjb | July, 2020

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pybaseball import statcast_batter
import xgboost as xgb
from feature_builder import *

playerid_reference = pd.read_csv("../data/playeridmap.csv")
label_encoding = ['double', 'field_out', 'home_run', 'single', 'triple']

def download_leaderboard_table(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    found = soup.find(
        "table", {"class": "rgMasterTable", "id": "LeaderBoard1_dg1_ctl00"}
    )
    stats_df = pd.read_html(str(found))[0]
    stats_df.columns = stats_df.columns.droplevel()
    return stats_df[:-1]


class woba_calculator:
    """
    object to collect wOBA coefficients
    Defaults are 2018 data
    """

    def __init__(
        self, wBB=0.690, wHBP=0.720, w1B=0.880, w2B=1.247, w3B=1.578, wHR=2.031
    ):

        self.wBB = wBB
        self.wHBP = wHBP
        self.w1B = w1B
        self.w2B = w2B
        self.w3B = w3B
        self.wHR = wHR

    def evaluate_events(self, bb, hbp, s, d, t, hr, ab, sf) -> float:
        # Evaluate woba given events
        return (
            self.wBB * bb
            + self.wHBP * hbp
            + self.w1B * s
            + self.w2B * d
            + self.w3B * t
            + self.wHR * hr
        ) / (ab + bb + hbp + sf)


class player_outcomes:
    """object to aggregate outcomes from player ID"""

    def __init__(self, playerid, start="2019-03-01", end="2019-11-03"):

        # Wrangle the DF
        player = statcast_batter(start, end, playerid)
        player = player[~player["events"].isna()]  # Drop nas
        player = player[player["game_type"] == "R"]  # Regular Season games only

        # Add other features
        player = add_spray_angle(player)
        player = add_park_factors(player, 2018)
        player = add_sprint_speed(player, 2018)

        # Save the DF
        self.df = player
        self.model_input = player[['launch_speed',
                                   'launch_angle',
                                   'adj_spray_angle',
                                   '1b_park_factor',
                                   '2b_park_factor',
                                   '3b_park_factor',
                                   'hr_park_factor',
                                   'sprint_speed']]

        # keep playerid for later
        self.playerid = playerid

        # Keep year if consistent
        if start.split("-")[0] == end.split("-")[0]:
            self.year = start.split("-")[0]
        else:
            self.year = None

        # Set properties
        vc = player["events"].value_counts()

        # If an event hasn't happend, a KeyError will happen
        if "walk" in vc:
            self.bb = vc["walk"]
        else:
            self.bb = 0
        if "single" in vc:
            self.single = vc["single"]
        else:
            self.single = 0
        if "double" in vc:
            self.double = vc["double"]
        else:
            self.double = 0
        if "triple" in vc:
            self.triple = vc["triple"]
        else:
            self.triple = 0
        if "home_run" in vc:
            self.hr = vc["home_run"]
        else:
            self.hr = 0
        if "sac_fly" in vc:
            self.sf = vc["sac_fly"]
        else:
            self.sf = 0
        if "hit_by_pitch" in vc:
            self.hbp = vc["hit_by_pitch"]
        else:
            self.hbp = 0

        # Still need ABs from FG, set later
        self.fg_ab = None
        self.fg_woba = None
        

    def add_fg_woba(self, year):
        # Add woba from fangraphs

        # Download
        woba_table_url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season={year}&month=0&season1={year}&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate={year}-01-01&enddate={year}-12-31&sort=16,d&page=1_2000"
        df = download_leaderboard_table(woba_table_url)
        # Add playerID
        id_df = playerid_reference[["FANGRAPHSNAME", "MLBID"]]
        df = df.merge(
            playerid_reference, how="left", left_on="Name", right_on="FANGRAPHSNAME"
        )

        try:
            fg_player = df[df["MLBID"] == self.playerid]
            if len(fg_player) == 1:
                self.fg_woba = float(fg_player["wOBA"].iloc[0])
        except:
            print("Failed to get FG wOBA")

    def add_fg_ab(self, year):

        # Download
        ab_table_url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=0&season={year}&month=0&season1={year}&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate={year}-01-01&enddate={year}-12-31&page=1_2000"
        df = download_leaderboard_table(ab_table_url)

        # Add playerID
        id_df = playerid_reference[["FANGRAPHSNAME", "MLBID"]]
        df = df.merge(
            playerid_reference, how="left", left_on="Name", right_on="FANGRAPHSNAME"
        )
        try:
            fg_player = df[df["MLBID"] == self.playerid]
            if len(fg_player) == 1:
                self.fg_ab = float(fg_player["AB"].iloc[0])
        except:
            print("Failed to get FG AB")

    def eval_woba(self, woba_calculator) -> float:
        if self.fg_ab is None:
            print("Error: set FG wOBA first!")
            return 0
        else:
            return (
                woba_calculator.wBB * self.bb
                + woba_calculator.wHBP * self.hbp
                + woba_calculator.w1B * self.single
                + woba_calculator.w2B * self.double
                + woba_calculator.w3B * self.triple
                + woba_calculator.wHR * self.hr
            ) / (self.fg_ab + self.bb + self.hbp + self.sf)


    def eval_model(self, model_path):
        # Load the model
        model = xgb.XGBClassifier()
        self.model = model.load_model(model_path)
        # Evaluate Model predictions
        response = model.predict_proba(self.model_input)
        
        for idx in range(0, len(label_encoding)):
            self.df[f"{label_encoding[idx]}_prob"] = response[:,idx]


    def eval_model_woba(self, woba_calculator):
        if (self.fg_ab==None):
            raise ValueError("fg_ab not set")

        print(self.df["single_prob"].sum())
        print(self.fg_ab )
        print(self.bb)
        print(woba_calculator.w2B)

        return ((woba_calculator.wBB * self.bb
            + woba_calculator.wHBP * self.hbp
            + woba_calculator.w1B * self.df["single_prob"].sum()
            + woba_calculator.w2B * self.df["double_prob"].sum()
            + woba_calculator.w3B * self.df["triple_prob"].sum()
            + woba_calculator.wHR * self.df["home_run_prob"].sum()
            ) / (self.fg_ab + self.bb + self.hbp + self.sf))