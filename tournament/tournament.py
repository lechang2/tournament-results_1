#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches")
    db.commit()
    db.close()
    """Remove all the match records from the database."""


def deletePlayers():
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM players")
    db.commit()
    db.close()
    """Remove all the player records from the database."""


def countPlayers():
    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM players")   #count the column of players
    number = c.fetchall()
    db.close()
    return int(number[0][0])   
    """Returns the number of players currently registered."""


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db= connect()
    c = db.cursor()
    c.execute("INSERT INTO players(player) VALUES(%s)" ,(name, ))
    db.commit()
    db.close()




def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()

    # 1. create list 'a' that contains a left joint winner list from players and matches based on winner id. wins and draws are counted using condition draw
    # 2. create list 'b' that contains a left joint loser list from players and matches based on loser id. wins and draws are counted using condition draw
    # 3. join a and b. count the matches by suming a.wins, b.loses, a.draws, b,draws. 
    query= '''CREATE VIEW no_OMW   
            AS SELECT a.id AS id, a.name AS name, a.wins AS wins, b.loses+a.wins+a.draws+b.draws AS matches,   
            a.draws+b.draws AS draws 
            FROM
                (SELECT                                                                                        
                    players.id AS id, players.player AS name, 
                    count(case WHEN draw='f' THEN 1 END) AS wins,
                    count(case WHEN draw='t' THEN 1 END) AS draws
                    FROM 
                        players LEFT JOIN matches ON players.id=matches.winner GROUP BY players.id)            
                AS a
                LEFT JOIN
                (SELECT 
                    players.id AS id, players.player AS name,                                                   
                    count(case WHEN draw='f' THEN 1 END) AS loses,
                    count(case WHEN draw='t' THEN 1 END) AS draws
                    FROM 
                        players LEFT JOIN matches on players.id=matches.loser GROUP BY players.id)         
                AS b
                ON a.id=b.id
            ORDER BY wins DESC, draws DESC
        '''
    c.execute(query)

    #1. combines table (winner, losers) with (losers, winers) as 'a' using union all. This creats a list of all players and their opponents. play id can repeat
    #2. create a 'b' list from no_OMW list with (oppoent, wins) 
    #3. join 'a', 'b' to get (player, opponent, opponent_win) list of 'c', however, this c has repeating players
    #4. sum the opponent_win from list 'c' group by player id from c to get (player, omw) list as VIEW OMW
    query1='''CREATE VIEW OMW AS
            SELECT c.player AS player, sum(c.OW) AS omw 
            FROM             
                ((SELECT loser AS player, winner AS opponent
                    FROM matches                                              
                    UNION ALL                                                 
                        SELECT winner AS player, loser AS opponent
                        FROM matches)  
                AS a  
                LEFT JOIN                                                    
                (SELECT no_OMW.id AS opponent, no_OMW.wins AS OW 
                    FROM no_OMW)  
                AS b     
                ON a.opponent=b.opponent) 
            AS c
            GROUP BY c.player                                                 
            '''
    c.execute(query1)


    # combine the (player, name, wins, matches, draws) list with (player, OMW) list
    query2= '''SELECT no_OMW.id AS id, no_OMW.name AS name, no_OMW.wins AS wins, no_OMW.matches AS matches, no_OMW.draws AS draws, OMW.omw AS omw
                FROM no_OMW LEFT JOIN OMW on no_OMW.id=OMW.player
                ORDER BY wins DESC, omw DESC
            '''
    c.execute(query2)
    result = c.fetchall()
    db.close()
    print result

    return result


def reportMatch(winner, loser, draw = False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    # draw is default False, if user select True, the match is a draw
    c.execute("INSERT INTO matches(winner,loser, draw) VALUES(%s, %s, %s)", (winner, loser, draw))
    db.commit()
    db.close()
    return
 
 
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
    standing = playerStandings()
    i = 0
    pairing = []
    # assumes event number of players. Take the players two by two from the standings list
    while i < len(standing):
        pairing.append((standing[i][0],standing[i][1],standing[i+1][0],standing[i+1][1]))
        i=i+2
    return pairing




