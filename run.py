#!/usr/bin/python3

import os, sys, json, random, time, pickle

# http://bottlepy.org
try:
    import bottle
except ImportError:
    import util.bottle as bottle
bottle.debug(True)

sys.path.append(os.path.dirname(__file__))

import cgi
import maze
from util.objectregister import ObjectRegister

class AbortVisit(Exception):
    pass


def grow(mymaze,x,y,radius):
    posns = [(x+dx,y+dy) for dx in range(-radius,1+radius) for dy in range(-radius,1+radius)]
    mymaze.random.shuffle(posns)
    [mymaze[x,y] for (x,y) in posns]


def visit(mymaze, x=0, y=0, iterations=10000):

    def setchoice(set):
        choice = mymaze.random.randint(0, len(set)-1)
        for i,x in enumerate(set):
            if i==choice:
                return x

    highlight = mymaze[0,0].colour

    visited = set()
    finished = set()
    for radius in range(3):
        grow(mymaze,x,y,radius)
    for i in range(iterations):
        if (i % 20000 == 10000):
            open('out/%s-%s.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
            print("eB=%f, after %d iterations, %d visited, %d finished" % (mymaze.pExtendBias, i, len(visited), len(finished)))

        visited.add((x,y))
        choices = list( maze.Maze.DIRECTIONS )
        choices.append( maze.Cell.EAST ) 
        choices.append( maze.Cell.EAST ) 
        choices.append( maze.Cell.EAST ) 
        choices.append( maze.Cell.EAST ) 
        
        try:
            mycell = mymaze[x,y]
        except maze.WalledIn as e:
            raise AbortVisit("eB=%f, walled in at %d" % (mymaze.pExtendBias, i))

        while choices:
            dirn = choices.pop(mymaze.random.randint(0,len(choices)-1))
            if mycell.isConnected(dirn):
                if dirn == maze.Cell.NORTH:   nx, ny = x, y-1
                elif dirn == maze.Cell.SOUTH: nx, ny = x, y+1
                elif dirn == maze.Cell.EAST:  nx, ny = x+1, y
                elif dirn == maze.Cell.WEST:  nx, ny = x-1, y
                if (nx,ny) not in visited and (nx,ny) not in finished:
                    break
        else:
            finished.add((x,y))
            visited.remove((x,y))
            if len(visited)==0:
                raise AbortVisit("eB=%f, totally walled in at %d" % (mymaze.pExtendBias, i))
            else:
                nx,ny = setchoice(visited)

        x,y = nx,ny

        try:
            grow(mymaze,x,y,2)
        except maze.WalledIn as e:
            # let the walker discover that
            pass

    return x,y




@bottle.route('/map/<x:int>/<y:int>')
def getMap(x=0, y=0):
        mymaze = pickle.load( open( 'maze.pickle', 'rb' ) )

        nx, ny = visit(mymaze, x, y,100)

        bottle.response.status = 200
        bottle.response.set_header('Content-Type', 'image/png')
        bottle.response.set_header('Refresh', '1; url=/map/%d/%d' % (nx, ny))

        output = mymaze.png(mymaze[0,0].colour)

        pickle.dump( mymaze, open( 'maze.pickle.new', 'wb' ) )
        os.rename( 'maze.pickle.new', 'maze.pickle' )

        return output


if __name__=="__main__":
    ObjectRegister( { "Maze": maze.Maze,
                      "Cell": maze.Cell
                    })

    runBottle = False
    mymaze = None

    a = list(sys.argv)
    a.pop(0)
    while a:
        x = a.pop(0)
        if x=='--seed':
            seed = int(a.pop(0))
            mymaze = maze.Maze(seed, pExtendBias=0.6, pExtendSensitivity=1.0, pUnifyLower=1.0, pMakeLoop=1.0)
            for i in range(10):
                grow(mymaze,0,0,i)
            pickle.dump( mymaze, open( 'maze.pickle', 'wb' ) )

        elif x=='--bottle':
            runBottle = True

        elif x=='--visit':
            iterations = int(a.pop(0))
            if mymaze is None:
                mymaze = pickle.load( open( 'maze.pickle', 'rb' ) )
            visit(mymaze,0,0,iterations)
            pickle.dump( mymaze, open( 'maze.pickle', 'wb' ) )

    if not os.path.isfile( 'maze.pickle' ):
        raise Exception('You must specify --seed if there is no existing pickled maze')

    if runBottle:
        bottle.run(host='localhost', port=8080)
    else:
        if mymaze is None:
            mymaze = pickle.load( open( 'maze.pickle', 'rb' ) )
        open('out.png','wb').write(mymaze.png(mymaze[0,0].colour))
        
        
