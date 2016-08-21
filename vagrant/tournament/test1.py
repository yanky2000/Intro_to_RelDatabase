from tournament import *


def testing():
    DB = connect()
    c = DB.cursor()
    wins_sql = "SELECT players.id AS id, count(matches.match_id) AS num " \
                   "FROM players left JOIN matches " \
                   "ON matches.winner_id = players.id " \
                   "GROUP BY players.id "

    losses_sql = "SELECT id, count(matches.match_id) AS num " \
                     "FROM players left JOIN matches " \
                     "ON players.id = matches.loser_id " \
                     "GROUP BY players.id "

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
              "JOIN matches_played "
                "ON players.id = matches_played.id "
              ";")
    matches = c.fetchall()
    # print "MATCHES :", matches
    DB.close()
    return matches



def pairs():
    DB = connect()
    c = DB.cursor()


    c.execute("SELECT id, loser_id FROM players, matches "
              "WHERE players.id = matches.winner_id "
              "ORDER BY id, loser_id ASC ;")
    pairs = c.fetchall()
    DB.close()
    return pairs


def ids():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id FROM players;")
    results = c.fetchall()
    DB.close()
    return results


deleteMatches()
deletePlayers()
registerPlayer("Bruno Walton")
registerPlayer("Boots O'Neal")
registerPlayer("Cathy Burton")
registerPlayer("Diane Grant")
# standings = playerStandings()
# standings = testing()
ids = ids()
# print "STANDINGS BEFORE: ", ids
[id1, id2, id3, id4] = [row[0] for row in ids]
# reportMatch(101, 102)
# reportMatch(101, 102)
reportMatch(id1, id2)
reportMatch(id3, id4)
reportMatch(id1, id3)
reportMatch(id2, id4)
# testing()
print pairs()
print testing()