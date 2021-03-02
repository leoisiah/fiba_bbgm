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
	"Nationality" TEXT, 
	"Nationality2" TEXT,
	"NationalTeam" TEXT,
	"College" TEXT, 
	PRIMARY KEY ("Id"),
	FOREIGN KEY ("Pos") REFERENCES "Position"("Pos")
);

CREATE TABLE "Team" (
	"Name" TEXT, 
	"ISO3" TEXT, 
	"ISO2" TEXT, 
	"Rank" INTEGER,
	PRIMARY KEY ("Name")
);

CREATE TABLE "Advanced_Stats" (
	"StatId" INTEGER, 
	"Competition" TEXT, 
	"YR" INTEGER, 
	"PlayerId" INTEGER,  
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
	PRIMARY KEY ("StatId", "Competition", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id")
);

CREATE TABLE "Misc_Stats" (
	"StatId" INTEGER, 
	"Competition" TEXT, 
	"YR" INTEGER, 
	"PlayerId" INTEGER,  
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
	PRIMARY KEY ("StatId", "Competition", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id")
);

CREATE TABLE "Per_36" (
	"StatId" INTEGER, 
	"Competition" TEXT, 
	"YR" INTEGER, 
	"PlayerId" INTEGER,  
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
	PRIMARY KEY ("StatId", "Competition", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id")
);

CREATE TABLE "Raw_Ratings" (
	"StatId" INTEGER, 
	"Competition" TEXT, 
	"YR" INTEGER, 
	"PlayerId" INTEGER, 	
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
	PRIMARY KEY ("StatId", "Competition", "YR"), 
	FOREIGN KEY ("PlayerId") REFERENCES "Player"("Id")
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
p36.StatId, p36.Competition, p36.YR, p36.PlayerId,  
p36.GP*p36.MIN as TOTMIN
from Per_36 p36, Misc_Stats misc, Advanced_Stats adv, Player p, Position pos
where p36.StatId = misc.StatId
and p36.StatId = adv.StatId
and p36.Competition = misc.Competition
and p36.Competition = adv.Competition 
and p36.YR = misc.YR
and p36.YR = adv.YR
and p36.PlayerId = p.Id
and p.Pos = pos.Pos;

create view Overall as
select 
StatId, Competition, YR, PlayerId,
(2*Str+3*Spd+Jmp+2*End+Ins+Dnk+FT+"2Pt"+2*"3Pt"+3*oIQ+4*dIQ+2*Drb+2*Pss+Reb)/26 as OVR 
from Raw_Ratings;

create view Adjustment_NBA as
select 
sub.Competition as subCompetition, 
sub.YR as subYR, 
main.Competition as mainCompetition, 
main.YR as mainYR,
(AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR)) as slope, 
-MIN(sub.OVR)*(AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR))+MIN(main.OVR) as intercept
from Overall sub, Overall main
where sub.PlayerId = main.PlayerId
and main.Competition = 'NBA' and main.YR = (select min(YR) from Per_36 where Competition = 'NBA')
group by sub.Competition, sub.YR, main.Competition, main.YR
having count(1) > 3;

create view Adjustment_DLeague as
select 
sub.Competition as subCompetition, 
sub.YR as subYR, 
main.Competition as mainCompetition, 
main.YR as mainYR,
(AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR)) as slope, 
-MIN(sub.OVR)*(AVG(main.OVR)-MIN(main.OVR))/(AVG(sub.OVR)-MIN(sub.OVR))+MIN(main.OVR) as intercept
from Overall sub, Overall main
where sub.PlayerId = main.PlayerId
and main.Competition = 'DLeague' and main.YR = (select min(YR) from Per_36 where Competition = 'DLeague')
group by sub.Competition, sub.YR, main.Competition, main.YR
having count(1) > 3;

create view Adjustment as
select * from Adjustment_NBA
UNION
select dl.subCompetition, dl.subYR, nb.mainCompetition, nb.mainYR,
nb.slope*dl.slope, nb.slope*dl.intercept+nb.intercept
from Adjustment_DLeague dl, Adjustment_NBA nb
where dl.mainCompetition = nb.subCompetition and dl.mainYR = nb.subYR
and (dl.subCompetition, dl.subYR) not in (select subCompetition, subYR from Adjustment_NBA);

create view Adjusted_Ratings as
select 
PlayerId, 
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
        adj.subCompetition, 
        adj.subYR,
        adj.mainCompetition, 
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
        from Raw_Ratings raw, Adjustment adj
        where raw.Competition = adj.subCompetition
        and raw.YR = adj.subYR
)
group by PlayerId;

create view Output as
select * from
(
select * , IFNULL(NationalTeam, Nationality) as NationalTeam2,
ROW_NUMBER () OVER ( 
        PARTITION BY IFNULL(NationalTeam, Nationality)
        ORDER BY NationalTeam desc, (4*Hgt+2*Str+3*Spd+Jmp+2*End+Ins+Dnk+FT+"2Pt"+2*"3Pt"+3*oIQ+4*dIQ+2*Drb+2*Pss+Reb)/30  desc
) RowNum,
ROW_NUMBER () OVER ( 
        PARTITION BY IFNULL(NationalTeam, Nationality)
        ORDER BY NationalTeam asc,  (4*Hgt+2*Str+3*Spd+Jmp+2*End+Ins+Dnk+FT+"2Pt"+2*"3Pt"+3*oIQ+4*dIQ+2*Drb+2*Pss+Reb)/30  asc
) RowNumDesc
from Adjusted_Ratings a, Player p
where p.Id = a.PlayerId
and (p.NationalTeam is not null or p.Nationality2 is NULL)
) where RowNum <= 12
and RowNum+RowNumDesc >= 9;