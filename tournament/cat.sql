-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


CREATE TABLE players ( id SERIAL primary key,
                     player TEXT,
                     wins INTEGER,
                     matchies INTEGER);

CREATE TABLE matches (match_id SERIAL,
					 winner SERIAL references players(id),
					 loser SERIAL references players(id)
					 round_id SERIAL, 
					 primary key(match_id, round_id));



