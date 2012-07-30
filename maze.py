#!/usr/bin/python3

import random
import util.hsv
import io, util.png

class WalledIn(Exception):
    pass

class Colour:
    def __init__(self, id):
        self.id = id
        self.delegate = self
        self.group = Group()

    def rgb(self, highlight=None):
        if highlight is None or self.getDelegate() is highlight.getDelegate():
            return util.hsv.hsvtorgb(self.id * 15, 1, 1)
        else:
            return 255,255,255

    def getDelegate(self):
        if self.delegate is not self:
            self.delegate = self.delegate.getDelegate()
        return self.delegate

    def getGroup(self):
        return self.getDelegate().group

    def unify(self, other):
        mine = self.getDelegate()
        yours = other.getDelegate()
        if mine is not yours:
            mine.delegate = yours
            yours.group.extend(mine.group)
            mine.group = None

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self


class Group:
    def __init__(self):
        self.liberties = 0

    def extend(self, other):
        # The liberties corresponding to the places groups abut have already been removed
        self.liberties += other.liberties

class Cell:
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

    def __init__(self,colour=None,connections=0):
        '''
        connections is an integer that records the set of connections in a private way.
        '''
        self.colour = colour
        self.connections = 0

    def obj(self):
        return { "colour": self.colour,
                 "connections": self.connections,
                 "__class__": "Cell" }

    def __repr__(self):
        return "Cell(%d)" % (self.colour)

    def svg(self, highlight=None):
        c = ''
        if (self.isConnected( Cell.NORTH )):
            c += '''<svg:line x1="0" y1="-0.25" x2="0" y2="-0.6"></svg:line>'''
        if (self.isConnected( Cell.SOUTH )):
            c += '''<svg:line x1="0" y1="0.25" x2="0" y2="0.6"></svg:line>'''
        if (self.isConnected( Cell.EAST )):
            c += '''<svg:line x1="0.25" y1="0" x2="0.6" y2="0"></svg:line>'''
        if (self.isConnected( Cell.WEST )):
            c += '''<svg:line x1="-0.25" y1="0" x2="-0.6" y2="0"></svg:line>'''



        b = '''<svg:g stroke-width="0.04" stroke="black">
    %s
</svg:g>
''' % c            

        b += '''<svg:g stroke-width="0.08" stroke="none">
    <svg:circle cx="0" cy="0" r="0.25" fill="rgb(%s)"></svg:circle>
</svg:g>
<!--svg:text x="0" y="0.1" font-size="0.3" fill="black" text-anchor="middle">%s</svg:text-->
''' % (','.join([str(c) for c in self.colour.rgb(highlight)]), self.colour.id)

        return b

    def addConnection(self,dirn):
        ''' '''
        self.connections = self.connections | (1 << dirn)

    def isConnected(self, dirn):
        ''' '''
        return self.connections & (1 << dirn)

    @staticmethod
    def oppositeDirection(dirn):
        ''' '''
        return dirn ^ 1








class Maze:

    DIRECTIONS = (Cell.NORTH,Cell.SOUTH,Cell.EAST,Cell.WEST)

    def __init__(self, seed=142857, pExtendBias=0.3, pExtendSensitivity=1.0, pUnifyLower=1.0, pMakeLoop=0.0):
        ''' '''
        self.grid = {} # (int, int) -> Cell
        self.numColours = 0
        self.random = random.Random(seed)
        self.pExtendBias = pExtendBias
        self.pExtendSensitivity = pExtendSensitivity
        self.pUnifyLower = pUnifyLower
        self.pMakeLoop = pMakeLoop

    def svg(self, highlight=None):
        ''' '''
        xl = min([coords[0] for coords in self.grid])-0.5
        yl = min([coords[1] for coords in self.grid])-0.5
        xr = max([coords[0] for coords in self.grid])+0.5
        yr = max([coords[1] for coords in self.grid])+0.5
        
        s = '<svg:svg xmlns:svg="http://www.w3.org/2000/svg" version="1.1" viewBox="%f %f %f %f">' % (xl, yl, (xr-xl*1.6), yr-yl)
#        print('Outputting svg for bbox %f,%f : %f,%f' % (xl, yl, xr, yr))
#        print(s)
        for (x, y), cell in self.grid.items():
#            print('Outputting svg for cell %d,%d' % (x, y))
            s+='<svg:g transform="translate(%f %f)">%s</svg:g>' % (x, y, self[x,y].svg(highlight))
        return s+'</svg:svg>'

    def png(self, highlight=None):
        xl = min([coords[0] for coords in self.grid])
        yl = min([coords[1] for coords in self.grid])
        xr = max([coords[0] for coords in self.grid])+1
        yr = max([coords[1] for coords in self.grid])+1

        pixels = [[0 for x in range(xl*6, xr*6)] for y in range(yl*2, yr*2)]
        
        def setPixel(x,y,r,g,b):
            pixels[y][x*3] = r
            pixels[y][x*3 + 1] = g
            pixels[y][x*3 + 2] = b

        for (x, y), cell in self.grid.items():
            r, g, b = cell.colour.rgb(highlight)
            dx = x - xl
            dy = y - yl
            setPixel(dx*2,dy*2,r,g,b)
            if cell.isConnected( Cell.NORTH ):
                setPixel(dx*2,dy*2-1,r,g,b)
            if cell.isConnected( Cell.SOUTH ):
                setPixel(dx*2,dy*2+1,r,g,b)
            if cell.isConnected( Cell.EAST ):
                setPixel(dx*2+1,dy*2,r,g,b)
            if cell.isConnected( Cell.WEST ):
                setPixel(dx*2-1,dy*2,r,g,b)

        for dx in range(xr-xl):
            for dy in range(yr-yl):
                x = dx + xl
                y = dy + yl
                try:
                    a = self.grid[x,y]
                    e = self.grid[x,y+1]
                    c = self.grid[x+1,y]
                    d = self.grid[x+1,y+1]
                    if a.isConnected( Cell.EAST ) and c.isConnected( Cell.SOUTH ) and d.isConnected( Cell.WEST ) and e.isConnected( Cell.NORTH ):
                        r,g,b = a.colour.rgb(highlight)
                        setPixel(dx*2+1,dy*2+1,r,g,b)
                except KeyError:
                    pass
            
        output = io.BytesIO()
        util.png.Writer( (xr-xl)*2, (yr-yl)*2 ).write( output, pixels )
        outBytes = output.getvalue()

        return outBytes
        

    def __getitem__(self,coords):
        ''' '''
        if coords not in self.grid:
            x, y = coords
            self.grid[coords] = self.generateCell(
                self.grid.get((x, y-1), None),
                self.grid.get((x, y+1), None),
                self.grid.get((x+1, y), None),
                self.grid.get((x-1, y), None),
            )
        return self.grid[coords]

    def generateCell(self, *neighbours):
        ''' '''
        north, south, east, west = neighbours
        self.numColours += 1
        colour = Colour(self.numColours) # Temporarily, the Cell gets its own Colour.
        cell = Cell(colour=colour)
        steps = list(zip(Maze.DIRECTIONS, neighbours))
        self.random.shuffle(steps)
        # Get liberties right.
        for dirn, other in steps:
            if other is None:
                colour.getGroup().liberties += 1
            else:
                other.colour.getGroup().liberties -= 1
                assert other.colour.getGroup().liberties >= 0, "Colour %s (in group %s) has %s liberties" % (other.colour.id, other.colour.getDelegate().id, other.colour.getGroup().liberties)

        makeLoop = self.random.random() < self.pMakeLoop
        # Make connections.
        for dirn, other in steps:
            if other is not None:
                oColour = other.colour
                if oColour.getGroup() is not colour.getGroup() or (makeLoop and oColour is cell.colour):
                    liberties = min(colour.getGroup().liberties, oColour.getGroup().liberties)
                    if self.pExtend(liberties) > self.random.random():
                        # Punch trough!
                        cell.addConnection(dirn)
                        other.addConnection(Cell.oppositeDirection(dirn))
                        # If there were a locked door between the Cells, it would be
                        # wrong to `unify()` here because the other Cell is not yet
                        # reachable. Delay calling `unify()` until key is reachable.
                        colour.unify(oColour)
                        # Choose a colour with bias.
                        chooseLower = self.random.random() < self.pUnifyLower
                        isLower = cell.colour < oColour
                        if chooseLower ^ isLower:
                            cell.colour = oColour

        if colour.getGroup().liberties == 0:
            raise WalledIn

        return cell

    def pExtend(self, liberties):
        '''
        Returns the probability of a group with `liberties` liberties punching through a given wall.
        '''
        return self.pExtendSensitivity/(1+liberties) + self.pExtendBias
