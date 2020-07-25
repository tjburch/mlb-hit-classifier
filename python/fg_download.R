#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

library(baseballr)

if (length(args) == 2){
        # Just pass some arb second arg for unqualified
        year = as.integer(args[1])
        leaderboards = fg_bat_leaders(x=year, y=year, league="all", qual="n")
        write.csv(leaderboards, paste("../data/uq_leaderboards",year,".csv"))
    } else if (length(args) == 1) {
        # Main functionality, pass year
        year = as.integer(args)
        print(paste("Downloading data from",year))
        leaderboards = fg_bat_leaders(x=year, y=year, league="all", qual="y")
        write.csv(leaderboards, paste("../data/leaderboards",year,".csv"))
    } else {
        # Default to 2018
        leaderboards = fg_bat_leaders(x=2018,y=2018, league="all", qual="y")
        write.csv(leaderboards, "../data/leaderboards2018.csv")
}
