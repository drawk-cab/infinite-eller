#!/usr/bin/python3

import os, sys, json, random, time
sys.path.append(os.path.dirname(__file__))

import cgi
import maze

class AbortVisit(Exception):
    pass

def visit(mymaze, iterations=10000):
    x = 0
    y = 0
    def grow(radius):
        posns = [(x+dx,y+dy) for dx in range(-radius,1+radius) for dy in range(-radius,1+radius)]
        mymaze.random.shuffle(posns)
        [mymaze[x,y] for (x,y) in posns]

    def setchoice(set):
        choice = mymaze.random.randint(0, len(set)-1)
        for i,x in enumerate(set):
            if i==choice:
                return x

    highlight = mymaze[0,0].colour

    visited = set()
    finished = set()
    for radius in range(3):
        grow(radius)
    for i in range(iterations):
        if (i % 20000 == 10000):
            open('out/%s-%08d.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
            print("eB=%f, after %d iterations, %d visited, %d finished" % (mymaze.pExtendBias, i, len(visited), len(finished)))

        visited.add((x,y))
        choices = list( maze.Maze.DIRECTIONS )
        
        try:
            mycell = mymaze[x,y]
        except maze.WalledIn as e:
            # teleport out
            # finished.add((x,y))
            # visited.remove((x,y))
            # if len(visited)==0:
            #   open('out/%s-%08d-walledin.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
            #   raise AbortVisit("eB=%f, totally walled in at %d" % (mymaze.pExtendBias, i))
            # else:
            #   nx,ny = setchoice(visited)
            open('out/%s-%08d-walledin.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
            raise AbortVisit("eB=%f, maze generator reports walled in at %d" % (mymaze.pExtendBias, i))

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
            # teleport out
            finished.add((x,y))
            visited.remove((x,y))
            if len(visited)==0:
                open('out/%s-%08d-walledin.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
                raise AbortVisit("eB=%f, totally walled in at %d" % (mymaze.pExtendBias, i))
            else:
                nx,ny = setchoice(visited)

        x,y = nx,ny

        try:
            grow(2)
        except maze.WalledIn as e:
            # let the walker discover that
            pass



# For debugging, you can run this script from command line
if __name__=="__main__":

    for eB in (0.01,):
        mymaze = maze.Maze(12, pExtendBias=eB, pExtendSensitivity=1.0, pUnifyLower=1.0, pMakeLoop=0.5)

        if not os.path.isdir('out'):
            os.mkdir('out')

        try:        
            visit(mymaze, 10000000)
        except AbortVisit as e:
            print("%s: %s" % (e.__class__.__name__, e))
        except Exception as e:
            open('out/%s-error.png' % (mymaze.pExtendBias),'wb').write(mymaze.png(mymaze[0,0].colour))
            raise e


        del(mymaze)

