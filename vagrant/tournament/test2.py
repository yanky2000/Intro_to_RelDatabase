from tournament import *

def t():
    DB = connect()
    c = DB.cursor()

    c.execute("create view all_plays as select id1 as id, match_id from matches "
              "UNION ALL "
              "SELECT id2 as id, match_id from matches ;")
    c.execute("select id, count(match_id) as games from all_plays "
              "GROUP by id "
              "ORDER by id asc ;")
    print "games: ", c.fetchall()
    DB.close()

t()
