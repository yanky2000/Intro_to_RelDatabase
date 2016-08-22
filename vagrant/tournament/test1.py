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

    wins_sql = "SELECT players.id AS id, count(matches.match_id) AS num " \
               "FROM players left JOIN matches " \
               "ON matches.winner_id = players.id " \
               "GROUP BY players.id " \
               "ORDER BY num desc "
    c.execute("CREATE VIEW wins as {0} ;".format(wins_sql))
    c.execute("select * from wins ORDER BY id ASC ;")
    print
    print "WINS : ", c.fetchall()

    c.execute("select * from wins ORDER BY num DESC, id ASC ;")
    print "WINS : ", c.fetchall()
    print



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
    c.execute("select id1, id2 from tpairs ;")
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
                      "id1 = {p[1]} OR "
                      "id2 = {p[1]} ;"
                      "".format(p=pair))
            print "One pair deleted"
            DB.commit()
            c.execute("select id1, id2 from tpairs ;")
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


def ids():
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id FROM players;")
    results = c.fetchall()
    DB.close()
    return results


def t():
    DB = connect()
    c = DB.cursor()
    c.execute("create view wins as SELECT players.id, count(match_id) as wins from players "
              "left join matches "
              "on players.id = matches.winner_id "
              "GROUP BY players.id ;")
    # c.execute("create view wins as SELECT winner_id as id, COUNT(match_id) as wins from matches "
    #           "GROUP BY winner_id ;")
    c.execute("select * from wins ;")
    print "wins: ", c.fetchall()

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

deleteMatches()
deletePlayers()
registerPlayer("Bruno Walton")
registerPlayer("Jin Heys")
registerPlayer("Sandy Walton")
registerPlayer("Boots O'Neal")
registerPlayer("Cathy Burton")
registerPlayer("Diane Grant")
# standings = playerStandings()
# standings = testing()
ids = ids()
# print "STANDINGS BEFORE: ", ids
[id1, id2, id3, id4, id5, id6] = [row[0] for row in ids]
# reportMatch(101, 102)
# reportMatch(101, 102)
reportMatch(id1, id3)
reportMatch(id4, id2)
reportMatch(id6, id5)
# testing()
# pairs()
# print testing()
t()