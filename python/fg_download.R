#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

library(baseballr)

if (length(args) == 1){
    year = as.integer(args)
    print(paste("Downloading data from",year))
    leaderboards = fg_bat_leaders(x=year, y=year, league="all", qual="y")
} else{
    # Default to 2018
    leaderboards = fg_bat_leaders(x=2018,y=2018, league="all", qual="y")
}
write.csv(leaderboards, "../data/leaderboards.csv")
