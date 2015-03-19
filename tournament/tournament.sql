-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players ( id SERIAL primary key, player TEXT);
-- id of the player and the name

CREATE TABLE matches (match_id SERIAL primary key, winner SERIAL references players(id),loser SERIAL references players(id), draw BOOLEAN);
-- matches has id is primary key, winner, loser and draw. Draw is defalt to be False. If True, both winner and looser are draw.



