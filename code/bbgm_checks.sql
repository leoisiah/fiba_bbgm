select * from
(select Competition, YR, count(*) CNT from Per_36 group by Competition, YR) a
,
(select Competition, YR, count(*) CNT from Advanced_Stats group by Competition, YR) b
,
(select Competition, YR, count(*) CNT from Misc_Stats group by Competition, YR) c
where
a.Competition = b.Competition
and
a.Competition = c.Competition
and
a.YR = b.YR
and
a.YR = c.YR
and
(a.CNT<>b.CNT OR a.CNT<>c.CNT OR b.CNT<>c.CNT);

select count(1) from Per_36;
select count(1) from Advanced_Stats;
select count(1) from Misc_Stats;

select * from Per_36 where PlayerId not in (select Id from Player where Player is not null) order by Competition;
select distinct Pos from Player;

select * from Output
where NationalTeam2 not in (select Name from Team);

