-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players(
  player_name TEXT,
  id  SERIAL PRIMARY KEY
);

CREATE TABLE matches(
  winner_id SERIAL REFERENCES players(id),
  loser_id SERIAL REFERENCES players(id),
  match_id  SERIAL PRIMARY KEY
  -- add restriction: winner could be chosen only from match players
);

-- CREATE TABLE standings(
--   id SERIAL REFERENCES players,
--   wins INT,
--   matches INT
-- );

