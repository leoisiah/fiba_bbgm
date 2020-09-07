PRAGMA foreign_keys = ON;

CREATE TABLE "Position" (
	"Pos" TEXT, 
	"PosValue" REAL,
	PRIMARY KEY ("Pos")
);

CREATE TABLE "Player" (
	"Id" INTEGER, 
	"Player" TEXT, 
	"Pos" TEXT, 
	"HT" INTEGER, 
	"WT" REAL, 
	"Birth City" TEXT, 
	"Birth Date" TIMESTAMP, 
	"Pre-NBA Draft Team" TEXT, 
	"Nationality" TEXT, 
	"Nationality2" TEXT, 
	"College" TEXT, 
	PRIMARY KEY ("Id"),
	FOREIGN KEY ("Pos") REFERENCES "Position"("Pos")
);

CREATE TABLE "Team" (
	"Name" TEXT, 
	"IOC3" TEXT, 
	"IOC2" TEXT, 
	"Rank" INTEGER,
	PRIMARY KEY ("Name")
);

CREATE TABLE "Competition" (
	"Id" INTEGER, 
	"Name" TEXT,
	PRIMARY KEY ("Id")
);

CREATE TABLE "Advanced_Stats" (
	"PlayerId" INTEGER, 
	"Player" TEXT, 
	"Team" TEXT, 
	"Pos" TEXT, 
	"TS%" REAL, 
	"eFG%" REAL, 
	"Total S %" REAL, 
	"ORB%" REAL, 
	"DRB%" REAL, 
	"TRB%" REAL, 
	"AST%" REAL, 
	"TOV%" REAL, 
	"STL%" REAL, 
	"BLK%" REAL, 
	"USG%" REAL, 
	"PPR" REAL, 
	"PPS" REAL, 
	"ORtg" REAL, 
	"DRtg" REAL, 
	"FIC" REAL, 
	"PER" REAL, 
	"CompetitionId" INTEGER, 
	"YR" INTEGER,
	PRIMARY KEY ("PlayerId", "Team", "CompetitionId", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id"),
	FOREIGN KEY ("Team") REFERENCES "Team"("Name"),
	FOREIGN KEY ("CompetitionId") REFERENCES "Competition"("Id")
);

CREATE TABLE "Misc_Stats" (
	"PlayerId" INTEGER, 
	"Player" TEXT, 
	"Team" TEXT, 
	"Pos" TEXT, 
	"Dbl Dbl" INTEGER, 
	"Tpl Dbl" INTEGER, 
	"40 Pts" INTEGER, 
	"20 Reb" INTEGER, 
	"20 Ast" INTEGER, 
	"5 Stl" INTEGER, 
	"5 Blk" INTEGER, 
	"High Game" INTEGER, 
	"Techs" INTEGER, 
	"HOB" REAL, 
	"Ast/TO" REAL, 
	"Stl/TO" REAL, 
	"FT/FGA" REAL, 
	"W's" INTEGER, 
	"L's" INTEGER, 
	"Win %" REAL, 
	"OWS" REAL, 
	"DWS" REAL, 
	"WS" REAL, 
	"CompetitionId" INTEGER, 
	"YR" INTEGER,
	PRIMARY KEY ("PlayerId", "Team", "CompetitionId", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id"),
	FOREIGN KEY ("Team") REFERENCES "Team"("Name"),
	FOREIGN KEY ("CompetitionId") REFERENCES "Competition"("Id")
);

CREATE TABLE "Per_36" (
	"PlayerId" INTEGER, 
	"Player" TEXT, 
	"Team" TEXT, 
	"Pos" TEXT, 
	"GP" INTEGER, 
	"MIN" REAL, 
	"FGM" REAL, 
	"FGA" REAL, 
	"FG%" REAL, 
	"3PM" REAL, 
	"3PA" REAL, 
	"3P%" REAL, 
	"FTM" REAL, 
	"FTA" REAL, 
	"FT%" REAL, 
	"TOV" REAL, 
	"PF" REAL, 
	"ORB" REAL, 
	"DRB" REAL, 
	"REB" REAL, 
	"AST" REAL, 
	"STL" REAL, 
	"BLK" REAL, 
	"PTS" REAL, 
	"CompetitionId" INTEGER, 
	"YR" INTEGER,
	PRIMARY KEY ("PlayerId", "Team", "CompetitionId", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id"),
	FOREIGN KEY ("Team") REFERENCES "Team"("Name"),
	FOREIGN KEY ("CompetitionId") REFERENCES "Competition"("Id")
);

CREATE TABLE "Raw_Ratings" (
	"PlayerId" INTEGER, 
	"Team" TEXT, 
	"CompetitionId" INTEGER, 
	"YR" INTEGER, 
	"Hgt" REAL, 
	"Str" REAL, 
	"Spd" REAL, 
	"Jmp" REAL, 
	"End" REAL, 
	"Ins" REAL, 
	"Dnk" REAL, 
	"FT" REAL, 
	"2Pt" REAL, 
	"3Pt" REAL, 
	"oIQ" REAL, 
	"dIQ" REAL, 
	"Drb" REAL, 
	"Pss" REAL, 
	"Reb" REAL,
	PRIMARY KEY ("PlayerId", "Team", "CompetitionId", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id"),
	FOREIGN KEY ("Team") REFERENCES "Team"("Name"),
	FOREIGN KEY ("CompetitionId") REFERENCES "Competition"("Id")
);

create view Consolidated_Stats as
select 
p36.MIN,
p36.FGM-p36."3PM" as "2PM",
p36.FGA-p36."3PA" as "2PA",
COALESCE((p36.FGM-p36."3PM")/(p36.FGA-p36."3PA"), 0) as "2P%",
p36."3PM",
p36."3PA",
p36."3P%",
p36.FTM,
p36.FTA,
p36."FT%",
p36.TOV,
p36.PF,
p36.ORB,
p36.DRB,
p36.AST,
p36.STL,
p36.BLK,
misc."Ast/TO",
misc."Stl/TO",
misc."FT/FGA",
misc."Win %",
adv."TS%",
adv."eFG%",
adv."Total S %",
adv."ORB%",
adv."DRB%",
adv."TRB%",
adv."AST%",
adv."TOV%",
adv."STL%",
adv."BLK%",
adv."USG%",
adv.PPR,
adv.PPS,
adv.ORtg,
adv.DRtg,
adv.PER,
pos.PosValue,
p.HT,
COALESCE(p.WT, 2.7*p.HT) as WT,
p36.YR-1-strftime('%Y', p."Birth Date") as Age,
p36.PlayerId, p36.Team, p36.CompetitionId, p36.YR,
p36.GP*p36.MIN as TOTMIN
from Per_36 p36, Misc_Stats misc, Advanced_Stats adv, Player p, Position pos
where p36.PlayerId = misc.PlayerId
and p36.PlayerId = adv.PlayerId
and p36.Team = misc.Team
and p36.Team = adv.Team 
and p36.CompetitionId = misc.CompetitionId
and p36.CompetitionId = adv.CompetitionId 
and p36.YR = misc.YR
and p36.YR = adv.YR
and p36.PlayerId = p.Id
and p.Pos = pos.Pos;

create view Overall as
select 
PlayerId, 
Team,
CompetitionId, 
YR, 
(Str+Spd+Jmp+End+Ins+Dnk+FT+"2Pt"+"3Pt"+oIQ+dIQ+Drb+Pss+Reb)/14 as OVR 
from Raw_Ratings;

create view Adjustment as
select 
sub.CompetitionId as subCompetitionId, 
sub.YR as subYR, 
main.CompetitionId as mainCompetitionId, 
main.YR as mainYR,
COALESCE((AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR)),1) as slope, 
-MIN(sub.OVR)*COALESCE((AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR)),1)+MIN(main.OVR) as intercept
from Overall sub, Overall main
where sub.PlayerId = main.PlayerId
group by sub.CompetitionId, sub.YR, main.CompetitionId, main.YR;

create view Adjusted_Ratings as
select 
PlayerId, 
Team, 
CompetitionId, 
YR,
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
	adj.mainCompetitionId as CompetitionId, 
	adj.mainYR as YR,
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
	from Raw_Ratings raw, Adjustment adj
	where raw.CompetitionId = adj.subCompetitionId
	and raw.YR = adj.subYR
) x
group by PlayerId,Team,CompetitionId,YR;