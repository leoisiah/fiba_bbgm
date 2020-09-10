# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:28:39 2020

@author: Leo Isiah
"""

import pandas;
import sqlite3;
import math;
import json;
#%%
def adjustRating(x):
    return min(max(round(x),0),100);

#%%
def computeWeight(ht, wt):
    if(math.isnan(wt)):
        return round(2.7*ht);
    return round(wt);

#%%
def computeBirthLoc(city, country):
    if(city is None):
        return country;
    return city+", "+country;

#%%
def computeCollege(college):
    if(college is None):
        return "";
    return college;

#%%
def generateJson(fileYear, conn):
    
    filename = str(fileYear-1)+"-"+str((fileYear)%100)+".FIBA.json"
    
    teamMap = {};
    confMap = {0:0, 1:1, 2:1, 3:0};
    divMap = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5, 6:5, 7:2, 8:1, 9:4, 10:3, 11:0}    
        
    crsr = conn.cursor();                        
    crsr.execute("drop view if exists Adjusted_Ratings");                        
    
    crsr.execute("""
        create view Adjusted_Ratings as
        select 
        PlayerId, 
        Team, 
        AVG(Hgt) as Hgt,
        AVG(Str) as Str,
        AVG(Spd) as Spd,
        AVG(Jmp) as Jmp,
        AVG(End) as End,
        AVG(Ins) as Ins,
        AVG(Dnk) as Dnk,
        AVG(FT) as FT,
        AVG("2Pt") as "2Pt",
        AVG("3Pt") as "3Pt",
        AVG(oIQ) as oIQ,
        AVG(dIQ) as dIQ,
        AVG(Drb) as Drb,
        AVG(Pss) as Pss,
        AVG(Reb) as Reb
        from
        (
        	select 
        	raw.PlayerId, 
        	raw.Team, 
        	adj.subCompetitionId, 
        	adj.subYR,
        	adj.mainCompetitionId, 
        	adj.mainYR,
        	raw.Hgt, 
        	raw.Str*adj.slope+adj.intercept as Str,
        	raw.Spd*adj.slope+adj.intercept as Spd,
        	raw.Jmp*adj.slope+adj.intercept as Jmp,
        	raw.End*adj.slope+adj.intercept as End,
        	raw.Ins*adj.slope+adj.intercept as Ins,
        	raw.Dnk*adj.slope+adj.intercept as Dnk,
        	raw.FT*adj.slope+adj.intercept as FT,
        	raw."2Pt"*adj.slope+adj.intercept as "2Pt",
        	raw."3Pt"*adj.slope+adj.intercept as "3Pt",
        	raw.oIQ*adj.slope+adj.intercept as oIQ,
        	raw.dIQ*adj.slope+adj.intercept as dIQ,
        	raw.Drb*adj.slope+adj.intercept as Drb,
        	raw.Pss*adj.slope+adj.intercept as Pss,
        	raw.Reb*adj.slope+adj.intercept as Reb
        	from Raw_Ratings raw, Adjustment adj, 
        	(
        		select CompetitionId, YR from Per_36
        		where YR between {fromYR} and {thruYR}
        		and CompetitionId in (1,2)
        		order by YR desc
        		limit 1
        	) x
        	where raw.CompetitionId = adj.subCompetitionId
        	and raw.YR = adj.subYR
        	and adj.mainCompetitionId = x.CompetitionId
        	and adj.mainYR = x.YR
        	and raw.YR between {fromYR} and {thruYR}            
        	and 
        	(
        	       (select count(1) from Raw_Ratings where Team=raw.Team and CompetitionId=adj.mainCompetitionId and YR = adj.mainYR) = 0
        	       OR
        	       (select count(1) from Raw_Ratings where Team=raw.Team and CompetitionId=adj.subCompetitionId and YR = adj.subYR) = 0
        	       OR
                        (select count(1) from Raw_Ratings r1, Raw_Ratings r2
                        where r1.Team=raw.Team and r1.CompetitionId=adj.mainCompetitionId and r1.YR = adj.mainYR
                        and r2.Team=raw.Team and r2.CompetitionId=adj.subCompetitionId and r2.YR = adj.subYR
                        and r1.PlayerId = r2.PlayerId) > 0
        	)                        
        )
        group by PlayerId,Team""".format(fromYR=fileYear-3, thruYR=fileYear-1))  
    
    teamsSql = pandas.read_sql(sql="""
        select * from Team 
        where Name in
        (
        select Team from Adjusted_Ratings
        group by Team
        having count(1) >= 10
        )
        order by Rank""", con=conn);
    
    teamsJson = [];
    
    for i, row in teamsSql.iterrows():           
        teamMap[row["Name"]] = i;
        teamJson = {"tid": i, "cid": confMap[i%4], "did": divMap[i%12], "region": row["IOC3"], "name": row["Name"], "abbrev": row["IOC3"], "imgURL": "https://www.countryflags.io/"+row["IOC2"]+"/shiny/64.png"}
        teamsJson.append(teamJson);
               
    playersSql = pandas.read_sql(sql="""
        select * from Player p, Adjusted_Ratings a
        where p.Id = a.PlayerId
        and a.Team in
        (
        select Team from Adjusted_Ratings
        group by Team
        having count(1) >= 10
        )
        order by a.Team""", con=conn);
   
    playersJson = [];
    
    for i, row in playersSql.iterrows():           
        playerJson = {"tid": teamMap[row["Team"]], 
                      "name": row["Player"], 
                      "ratings": [{"diq": adjustRating(row["dIQ"]), 
                                   "dnk": adjustRating(row["Dnk"]), 
                                   "drb": adjustRating(row["Drb"]), 
                                   "endu": adjustRating(row["End"]), 
                                   "fg": adjustRating(row["2Pt"]), 
                                   "ft": adjustRating(row["FT"]), 
                                   "hgt": adjustRating(row["Hgt"]), 
                                   "ins": adjustRating(row["Ins"]), 
                                   "jmp": adjustRating(row["Jmp"]), 
                                   "oiq": adjustRating(row["oIQ"]), 
                                   "pss": adjustRating(row["Pss"]), 
                                   "reb": adjustRating(row["Reb"]), 
                                   "spd": adjustRating(row["Spd"]), 
                                   "stre": adjustRating(row["Str"]), 
                                   "tp": adjustRating(row["3Pt"])}], 
                      "pos": row["Pos"], 
                      "hgt": row["HT"], 
                      "weight": computeWeight(row["HT"], row["WT"]), 
                      "born": {"year": int(row["Birth Date"][0:4]), "loc": computeBirthLoc(row["Birth City"], row["Nationality"])}, 
                      "college": computeCollege(row["College"]),
                      "contract":{"amount":30000,"exp":fileYear+30},}
        playersJson.append(playerJson);

        
    output = {"version":36, "startingSeason":fileYear, "players":playersJson, "teams":teamsJson, 
              "gameAttributes": [{"key": "aiTradesFactor", "value": 0}, {"key": "challengeNoTrades", "value": True}, {"key": "draftType", "value": "random"}, {"key": "foulsNeededToFoulOut", "value": 5}, {"key": "maxRosterSize", "value": 23}, {"key": "numSeasonsFutureDraftPicks", "value": 0}, {"key": "quarterLength", "value": 10}]}
        
    outJson = json.dumps(output, indent=4)
        
    with open(filename, "w") as fw:
        fw.write(outJson);
			
    print("OUTPUT: "+filename);    

    
#%%   
conn = sqlite3.connect('bbgm.db');

try:  
    for year in range(2013,2021): 
        generateJson(year, conn);    
finally:    
    conn.close();
