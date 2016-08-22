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
    c.execute("create view wins as SELECT players.id, count(match_id) as wins from players "
              "left join matches "
              "on players.id = matches.winner_id "
              "GROUP BY players.id ;")
    # c.execute("create view wins as SELECT winner_id as id, COUNT(match_id) as wins from matches "
    #           "GROUP BY winner_id ;")
    c.execute("select * from wins ;")
    # print "wins: ", c.fetchall()

    c.execute("create view all_plays as select id1 as id, match_id from matches "
              "UNION ALL "
              "SELECT id2 as id, match_id from matches ;")

    c.execute("create view games as select players.id, count(match_id) as games from players left join all_plays "
              "on players.id = all_plays.id "
              "GROUP by players.id "
              "ORDER by players.id asc ;")

    c.execute("select players.id, player_name, wins, games from "
              "players left JOIN wins "
              "on players.id = wins.id "
              "left join games on players.id = games.id "
              "order by wins desc, players.id asc ;")

    standings = c.fetchall()
    print standings
    c.execute("drop view games ;")
    c.execute("drop view all_plays ;")
    c.execute("drop view wins ;")
    DB.commit()
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
    if winner < loser:
        p1 = winner
        p2 = loser
    else:
        p1 = loser
        p2 = winner
    c.execute("INSERT INTO matches VALUES (%s, %s, %s) ;", (
        bleach.clean(p1),
        bleach.clean(p2),
        bleach.clean(winner),)
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
    DB = connect()
    c = DB.cursor()

    wins_sql = "SELECT players.id AS id, count(matches.match_id) AS num " \
               "FROM players left JOIN matches " \
               "ON matches.winner_id = players.id " \
               "GROUP BY players.id " \
               "ORDER BY num desc "
    c.execute("CREATE VIEW wins as {0} ;".format(wins_sql))
    c.execute("select * from wins ORDER BY id ASC ;")
    # print
    # print "WINS : ", c.fetchall()

    c.execute("select * from wins ORDER BY num DESC, id ASC ;")
    # print "WINS : ", c.fetchall()
    # print

    # get all possible pairs, that didn't play yet in id1 < id2 order.
    # c.execute("select a.id, b.id from wins as a, wins as b WHERE a.id != b.id and a.id < b.id ;")
    # print "pos pairs :", c.fetchall()

    c.execute("CREATE VIEW pos_pairs as "
              "select a.id as id1, b.id as id2 from wins as a, wins as b WHERE a.id != b.id and a.id < b.id "
              "EXCEPT "
              "SELECT id1, id2 from matches "
              "ORDER BY id1 ;")

    c.execute("create view pairs as Select id1, a.num as id1_wins, id2, b.num as id2_wins "
              "from pos_pairs, wins as a, wins as b "
              "WHERE id1=a.id and id2 = b.id "
              "ORDER BY a.num desc, id1 ASC, b.num DESC , id2 ASC "
              ";")

    # c.execute("select * from pairs ;")
    # print
    # print "Excepted Pairs & wins: ", c.fetchall()

    c.execute("create table tpairs( "
              "id1 SERIAL REFERENCES players,"
              "id2 serial REFERENCES players) ;")
    c.execute("insert into tpairs SELECT id1, id2 from pairs ;")
    # c.execute("select * from tpairs ;")
    # print
    # print "new table: ", c.fetchall()

    selected_pairs = []

    # Take first 2 top players and exclude them from possible pairs
    c.execute("select id1, a.player_name as name1, id2, b.player_name as name2 from tpairs join players as a "
              "on tpairs.id1=a.id "
              "join players as b "
              "on tpairs.id2 = b.id ;")
    pair = c.fetchone()
    # def pairs_to_play():
    #     DB = connect()
    #     c = DB.cursor()
    #     DB.close()
    #     return c.fetchone()

    tre = 0
    while pair:
        # pairs_to_play()
        # pair = pairs_to_play()
        # while pair:
        #     if cc > 10:
        #         break
        if tre > 10:
            break
        else:
            selected_pairs.append(pair)
            c.execute("delete from tpairs "
                      "where "
                      "id1 = {p[0]} OR "
                      "id2 = {p[0]} OR "
                      "id1 = {p[2]} OR "
                      "id2 = {p[2]} ;"
                      "".format(p=pair))
            # print "One pair deleted"
            DB.commit()
            c.execute("select id1, a.player_name as name1, id2, b.player_name as name2 from tpairs join players as a "
                      "on tpairs.id1=a.id "
                      "join players as b "
                      "on tpairs.id2 = b.id ;")
            pair = c.fetchone()
            # pair = c.fetchone()
            tre += 1

    c.execute("drop table tpairs;")
    c.execute("drop view wins CASCADE ;")
    # c.execute("drop view pairs CASCADE ;")
    # c.execute("drop view pos_pairs CASCADE ;")
    DB.commit()
    print
    print "Selected pairs: ", selected_pairs

    DB.close()
    return selected_pairs


