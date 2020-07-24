""" Aggregates all the wOBA data for the top 200 players
Sources from FG, Baseball Savant, and Model output
"""
from woba_evaluator import *
import csv
import tqdm

import pdb

# Argparse for year flexibility
import argparse
parser = argparse.ArgumentParser(description='Generate CSV with wOBA info')
parser.add_argument("-y","--year", type=int, default=2019, help="What year to evaluate")
parser.add_argument("-o","--output", type=str, default="../data/model_output.csv", help="Output File")
args = parser.parse_args()

#def generate_player(playerid):


playerid_reference = pd.read_csv("../data/playeridmap.csv")


def generate_outcomes(playerid):
    
    # Should automate scraping of woba constants
    wc = woba_calculator(
        wBB=0.690,
        wHBP=0.719,
        w1B=0.870,
        w2B=1.217,
        w3B=1.529,
        wHR=1.940
    )

    outcomes = Outcomes(playerid)
    outcomes.add_fg_woba(args.year)
    outcomes.add_fg_ab(args.year)
    outcomes.add_xwoba("../data/2019_xwoba.csv")
    outcomes.eval_model('../models/final_model')
    model_woba = outcomes.eval_model_woba(wc)
    return(outcomes, model_woba)

def update_data(year):
    # Download data using baseballR
    import subprocess
    returncode = subprocess.call(
        ["/usr/local/bin//Rscript",  # Local R executable
        "fg_download.R", # Script to download data from baseballR
        " {0}".format(year)] # Year command line argument
        )
    if returncode != 0:
        print("Nonzero return code on download - Data might not be updated.")


if __name__ == "__main__":
    
    # Get list of players we want
    # Qualified batters, top 100 by wOBA
    update_data(args.year)
    leaders = pd.read_csv("../data/leaderboards.csv")
    #leaders = download_leaderboard_table(
    #    f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=y&type=8&season={args.year}&month=0&season1={args.year}&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate={args.year}-01-01&enddate={args.year}-12-31&sort=16,d&page=1_140"
    #    )
    
    # Get Their MLBID
    leaders["playerid"] = leaders["playerid"].astype(str)
    leaders = leaders.merge(
        playerid_reference[["IDFANGRAPHS", "MLBID"]], how="left", left_on="playerid", right_on="IDFANGRAPHS"
    )

    # Open output file
    with open(args.output, 'w+') as csvfile:
        write = csv.writer(csvfile)
        # Write header line
        write.writerow([
            "idx","name", "playerid", "fg_woba", "model_woba", "xwoba",
            "bb","hbp","single","double","triple","hr",
            "p_single","p_double","p_triple","p_hr"])

        # Generate outcome object for each
        for i in tqdm.tqdm(range(len(leaders["MLBID"]))):
            playerid = leaders["MLBID"][i]
            outcomes, model_woba = generate_outcomes(playerid)
            write.writerow([
                i,
                leaders["Name"][i],
                int(playerid),  # keep both as cross-check
                outcomes.fg_woba,
                model_woba, 
                outcomes.xwoba,
                outcomes.bb,
                outcomes.hbp,
                outcomes.single,
                outcomes.double,
                outcomes.triple,
                outcomes.hr,
                outcomes.df["single_prob"].sum(),
                outcomes.df["double_prob"].sum(),
                outcomes.df["triple_prob"].sum(),
                outcomes.df["home_run_prob"].sum()])
            
            del outcomes # python GC should clean this up, but just to be safe
