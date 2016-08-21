#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(*) FROM players")
    num = c.fetchone()[0]
    DB.close()
    return num


def registerPlayer(name):

    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    SQL = "INSERT INTO players VALUES (%s)"
    bleached_name = bleach.clean(name)
    c.execute(SQL, (bleached_name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won_
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    wins_sql = "SELECT id, count(match_id) AS num " \
                   "FROM players left JOIN matches " \
                   "ON matches.winner_id = players.id " \
                   "GROUP BY id "

    losses_sql = "SELECT id, count(match_id) AS num " \
                     "FROM players left JOIN matches " \
                     "ON players.id = matches.loser_id " \
                     "GROUP BY id "

    # We will use wins view twice: for calculating total matches and getting a number of wins
    c.execute("CREATE VIEW wins as {0} ;".format(wins_sql))

    # we get total number of matches played by sum of wins and losses
    total_records = "".join([wins_sql, "UNION all ", losses_sql])
    c.execute("create view matches_played as "
                  "select id, sum(num) as games "
                      "from ({0}) as totals "
                      "group BY id ORDER BY id ;"
              .format(total_records))

    # Getting standing table
    c.execute("SELECT "
                "players.id, "
                "player_name, "
                "wins.num, "
                "games "
              "FROM players "
              "JOIN wins "
                "ON players.id = wins.id "
              "left JOIN matches_played "
                "ON players.id = matches_played.id "
              ";")
    standings = c.fetchall()
    DB.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO matches VALUES (%s, %s) ;", (
        bleach.clean(winner),
        bleach.clean(loser),)
    )
    DB.commit()
    DB.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


