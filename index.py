#!/usr/bin/python3

import os, sys, json, random, time
sys.path.append(os.path.dirname(__file__))

import cgi
import maze
from util.objectregister import ObjectRegister


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
        except Exception as e:
            # probably walled self in, teleport out (FIXME handle exception properly)
            finished.add((x,y))
            visited.remove((x,y))
            if len(visited)==0:
                open('out/%s-%s-walledin.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
                raise Exception("eB=%f, totally walled in at %d" % (mymaze.extendBias, i))
            else:
                nx,ny = setchoice(visited)

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
                open('out/%s-%s-walledin.png' % (mymaze.pExtendBias, i),'wb').write(mymaze.png(highlight))
                raise Exception("eB=%f, totally walled in at %d" % (mymaze.extendBias, i))
            else:
                nx,ny = setchoice(visited)

        x,y = nx,ny

        try:
            grow(2)
        except Exception as e:
            # probably walled self in, but let the walker discover that
            pass


class Application:

    def __init__(self, *args):
        # no idea what Apache is passing here
        self.initArgs = args

    def __call__(self,environ, start_response):
        query = cgi.parse_qs(environ['QUERY_STRING'])

        seed = query.get("seed",[12])[0]

        ObjectRegister( { "Maze": maze.Maze,
                          "Cell": maze.Cell
                        })

        mymaze = maze.Maze(seed)

        visit(mymaze)
        highlight = mymaze[0,0].colour

        try:
            status = '200 OK'
            output = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/html1/DTD/xhtml1-strict.dtd">
<html  xmlns="http://www.w3.org/1999/xhtml"
                     xmlns:svg="http://www.w3.org/2000/svg"
                     xmlns:xlink="http://www.w3.org/1999/xlink"
>
    <head>
        <title>%s</title>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    </head>
    <body onload="init()">
        %s
    </body>
</html>
''' % ("Maze", mymaze.svg(highlight))

        except Exception as e:
            status = '404 Not Found'

            output = '''<html  xmlns="http://www.w3.org/1999/xhtml">
    <head><title>404 Not Found</title></head>
    <body><h1>%s</h1><p>%s</p></body>
</html>
''' % (e.__class__.__name__, e)

        outBytes = output.encode("utf-8")

        response_headers = [('Content-type', 'application/xhtml+xml; charset=utf-8'),
                        ('Content-length', str(len(outBytes)))]

        start_response(status, response_headers)

        return [outBytes]


# Apache mod_wsgi is very weird
def application(environ, start_response):
    return Application().__call__(environ, start_response)

# For debugging, you can run this script from command line
if __name__=="__main__":
    ObjectRegister( { "Maze": maze.Maze,
                      "Cell": maze.Cell
                    })

    for eB in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        mymaze = maze.Maze(12, pExtendBias=eB, pExtendSensitivity=2.0, pUnifyLower=1.0)

        try:
            visit(mymaze, 100000)
        except Exception as e:
            print(e)

        time.sleep(30)
        del(mymaze)
