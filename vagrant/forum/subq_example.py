def lightweights(cursor):
    """Returns a list of the players in the db whose weight is less than the average."""
    # cursor.execute("select avg(weight) as av from players;")
    # av = cursor.fetchall()[0][0]  # first column of first (and only) row
    cursor.execute("select name, weight from players, (select avg(weight) as av from players) as sub where weight < av")
    return cursor.fetchall()