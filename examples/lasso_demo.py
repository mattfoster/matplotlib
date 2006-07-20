"""
Show how to use a lasso to select a set of points and get the indices
of the selected points.  A callback is used to change the color of the
selected points

This is currently a proof-of-concept implementation (though it is
usable as is).  There will be some refinement of the API and the
inside polygon detection routine.
"""
from matplotlib.widgets import Lasso
from matplotlib.mlab import inside_poly
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection

from pylab import figure, show, nx

class Datum:
    colorin = colorConverter.to_rgba('red')
    colorout = colorConverter.to_rgba('green')    
    def __init__(self, x, y, include=False):
        self.x = x
        self.y = y
        if include: self.color = self.colorin
        else: self.color = self.colorout
        
        
class LassoManager:
    def __init__(self, ax, data):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = data

        self.Nxy = len(data)

        self.facecolors = [d.color for d in data]
        self.xys = [(d.x, d.y) for d in data]

        self.collection = RegularPolyCollection(
            fig.dpi, 6, sizes=(100,),
            facecolors=self.facecolors,
            offsets = self.xys,
            transOffset = ax.transData)

        ax.add_collection(self.collection)

        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        
    def callback(self, verts):
        #print 'all done', verts
        ind = inside_poly(self.xys, verts)
        
        for i in range(self.Nxy):
            if i in ind:
                self.facecolors[i] = Datum.colorin
            else:
                self.facecolors[i] = Datum.colorout             

        self.canvas.draw_idle()

    def onpress(self, event):        
        if event.inaxes is None: return 
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)

data = [Datum(*xy) for xy in nx.mlab.rand(100, 2)]

fig = figure()
ax = fig.add_subplot(111, xlim=(0,1), ylim=(0,1), autoscale_on=False)
lman = LassoManager(ax, data)
    
show()