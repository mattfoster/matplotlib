"""
The OffsetBox is a simple container artist. The child artist are meant
to be drawn at a relative position to its parent.  The [VH]Packer,
DrawingArea and TextArea are derived from the OffsetBox.

The [VH]Packer automatically adjust the relative postisions of their
children, which should be instances of the OffsetBox. This is used to
align similar artists together, e.g., in legend.

The DrawingArea can contain any Artist as a child. The
DrawingArea has a fixed width and height. The position of children
relative to the parent is fixed.  The TextArea is contains a single
Text instance. The width and height of the TextArea instance is the
width and height of the its child text.
"""


import matplotlib.transforms as mtransforms
import matplotlib.artist as martist
import matplotlib.text as mtext
import numpy as np

from matplotlib.patches import bbox_artist as mbbox_artist
DEBUG=False
# for debuging use
def bbox_artist(*kl, **kw):
    if DEBUG:
        mbbox_artist(*kl, **kw)


# _get_packed_offsets() and _get_aligned_offsets() are coded assuming
# that we are packing boxes horizontally. But same function will be
# used with vertical packing.

def _get_packed_offsets(wd_list, total, sep, mode="fixed"):
    """
    Geiven a list of (width, xdescent) of each boxes, calculate the
    total width and the x-offset positions of each items according to
    *mode*. xdescent is analagous to the usual descent, but along the
    x-direction. xdescent values are currently ignored.
    
    *wd_list* : list of (width, xdescent) of boxes to be packed.
    *sep* : spacing between boxes
    *total* : Intended total length. None if not used.
    *mode* : packing mode. 'fixed', 'expand', or 'equal'.
    """

    w_list, d_list = zip(*wd_list)
    # d_list is currently not used.
    
    if mode == "fixed":
        offsets_ = np.add.accumulate([0]+[w + sep for w in w_list])
        offsets = offsets_[:-1]

        if total is None:
            total = offsets_[-1] - sep
            
        return total, offsets

    elif mode == "expand":
        sep = (total - sum(w_list))/(len(w_list)-1.)
        offsets_ = np.add.accumulate([0]+[w + sep for w in w_list])
        offsets = offsets_[:-1]

        return total, offsets

    elif mode == "equal":
        maxh = max(w_list)
        if total is None:
            total = (maxh+sep)*len(w_list)
        else:
            sep = float(total)/(len(w_list)) - maxh

        offsets = np.array([(maxh+sep)*i for i in range(len(w_list))])

        return total, offsets

    else:
        raise ValueError("Unknown mode : %s" % (mode,))


def _get_aligned_offsets(hd_list, height, align="baseline"):
    """
    Geiven a list of (height, descent) of each boxes, align the boxes
    with *align* and calculate the y-offsets of each boxes.
    total width and the offset positions of each items according to
    *mode*. xdescent is analagous to the usual descent, but along the
    x-direction. xdescent values are currently ignored.
    
    *hd_list* : list of (width, xdescent) of boxes to be aligned.
    *sep* : spacing between boxes
    *height* : Intended total length. None if not used.
    *align* : align mode. 'baseline', 'top', 'bottom', or 'center'.
    """

    if height is None:
        height = max([h for h, d in hd_list])

    if align == "baseline":
        height_descent = max([h-d for h, d in hd_list])
        descent = max([d for h, d in hd_list])
        height = height_descent + descent
        offsets = [0. for h, d in hd_list]
    elif align in ["left","top"]:
        descent=0.
        offsets = [d for h, d in hd_list]
    elif align in ["right","bottom"]:
        descent=0.
        offsets = [height-h+d for h, d in hd_list]
    elif align == "center":
        descent=0.
        offsets = [(height-h)*.5+d for h, d in hd_list]
    else:
        raise ValueError("Unknown Align mode : %s" % (align,))

    return height, descent, offsets



class OffsetBox(martist.Artist):
    """
    The OffsetBox is a simple container artist. The child artist are meant
    to be drawn at a relative position to its parent.  
    """
    def __init__(self, *kl, **kw):

        super(OffsetBox, self).__init__(*kl, **kw)
        
        self._children = []        
        self._offset = (0, 0)

    def set_figure(self, fig):
        """
        Set the figure

        accepts a class:`~matplotlib.figure.Figure` instance
        """
        martist.Artist.set_figure(self, fig)
        for c in self.get_children():
            c.set_figure(fig)
        
    def set_offset(self, xy):
        """
        Set the offset

        accepts x, y, tuple, or a callable object.
        """
        self._offset = xy

    def get_offset(self, width, height, xdescent, ydescent):
        """
        Get the offset

        accepts extent of the box
        """
        if callable(self._offset):
            return self._offset(width, height, xdescent, ydescent)
        else:
            return self._offset

    def set_width(self, width):
        """
        Set the width

        accepts float
        """
        self._width = width

    def set_height(self, height):
        """
        Set the height

        accepts float
        """
        self._height = height
        
    def get_children(self):
        """
        Return a list of artists it contains.
        """
        return self._children

    def get_extent_offsets(self, renderer):
        raise Exception("")

    def get_extent(self, renderer):
        """
        Return with, height, xdescent, ydescent of box
        """
        w, h, xd, yd, offsets = self.get_extent_offsets(renderer)
        return w, h, xd, yd

    def get_window_extent(self, renderer):
        '''
        get the bounding box in display space.
        '''
        w, h, xd, yd, offsets = self.get_extent_offsets(renderer)
        px, py = self.get_offset(w, h, xd, yd)
        return mtransforms.Bbox.from_bounds(px-xd, py-yd, w, h)

    def draw(self, renderer):
        """
        Update the location of children if necessary and draw them
        to the given *renderer*.
        """

        width, height, xdescent, ydescent, offsets = self.get_extent_offsets(renderer)

        px, py = self.get_offset(width, height, xdescent, ydescent)

        for c, (ox, oy) in zip(self.get_children(), offsets):
            c.set_offset((px+ox, py+oy))
            c.draw(renderer)

        bbox_artist(self, renderer, fill=False, props=dict(pad=0.))
    

class VPacker(OffsetBox):
    """
    The VPacker has its children packed vertically. It automatically
    adjust the relative postisions of children in the drawing time.
    """
    def __init__(self, pad=None, sep=None, width=None, height=None,
                 align="baseline", mode="fixed",
                 children=None):
        """
        *pad* : boundary pad
        *sep* : spacing between items
        *width*, *height* : width and height of the container box.
           calculated if None.
        *align* : alignment of boxes
        *mode* : packing mode
        """
        super(VPacker, self).__init__()

        self._height = height
        self._width = width
        self._align = align
        self._sep = sep
        self._pad = pad
        self._mode = mode
        
        self._children = children
        

    def get_extent_offsets(self, renderer):
        """
        update offset of childrens and return the extents of the box
        """

        whd_list = [c.get_extent(renderer) for c in self.get_children()]
        whd_list = [(w, h, xd, (h-yd)) for w, h, xd, yd in whd_list]


        wd_list = [(w, xd) for w, h, xd, yd in whd_list]
        width, xdescent, xoffsets = _get_aligned_offsets(wd_list,
                                                         self._width,
                                                         self._align)

        pack_list = [(h, yd) for w,h,xd,yd in whd_list]
        height, yoffsets_ = _get_packed_offsets(pack_list, self._height,
                                                self._sep, self._mode)
            
        yoffsets = yoffsets_  + [yd for w,h,xd,yd in whd_list]
        ydescent = height - yoffsets[0]
        yoffsets = height - yoffsets

        #w, h, xd, h_yd = whd_list[-1]
        yoffsets = yoffsets - ydescent

        return width + 2*self._pad, height + 2*self._pad, \
               xdescent+self._pad, ydescent+self._pad, \
               zip(xoffsets, yoffsets)



class HPacker(OffsetBox):
    """
    The HPacker has its children packed horizontally. It automatically
    adjust the relative postisions of children in the drawing time.
    """
    def __init__(self, pad=None, width=None, height=None, sep=None,
                 align="baseline", mode="fixed",
                 children=None):
        """
        *pad* : boundary pad
        *sep* : spacing between items
        *width*, *height* : width and height of the container box.
           calculated if None.
        *align* : alignment of boxes
        *mode* : packing mode
        """
        super(HPacker, self).__init__()

        self._height = height
        self._width = width
        self._align = align
        
        self._sep = sep
        self._pad = pad
        self._mode = mode

        self._children = children
        

    def get_extent_offsets(self, renderer):
        """
        update offset of childrens and return the extents of the box
        """

        whd_list = [c.get_extent(renderer) for c in self.get_children()]

        if self._height is None:
            height_descent = max([h-yd for w,h,xd,yd in whd_list])  
            ydescent = max([yd for w,h,xd,yd in whd_list])
            height = height_descent + ydescent
        else:
            height = self._height - 2*self._pad # width w/o pad

        hd_list = [(h, yd) for w, h, xd, yd in whd_list]
        height, ydescent, yoffsets = _get_aligned_offsets(hd_list,
                                                          self._height,
                                                          self._align)


        pack_list = [(w, xd) for w,h,xd,yd in whd_list]
        width, xoffsets_ = _get_packed_offsets(pack_list, self._width,
                                               self._sep, self._mode)

        xoffsets = xoffsets_  + [xd for w,h,xd,yd in whd_list]

        xdescent=whd_list[0][2]
        xoffsets = xoffsets - xdescent
        
        return width + 2*self._pad, height + 2*self._pad, \
               xdescent + self._pad, ydescent + self._pad, \
               zip(xoffsets, yoffsets)

        

class DrawingArea(OffsetBox):
    """
    The DrawingArea can contain any Artist as a child. The DrawingArea
    has a fixed width and height. The position of children relative to
    the parent is fixed.
    """
    
    def __init__(self, width, height, xdescent=0.,
                 ydescent=0., clip=True):
        """
        *width*, *height* : width and height of the container box.
        *xdescent*, *ydescent* : descent of the box in x- and y-direction.
        """

        super(DrawingArea, self).__init__()

        self.width = width
        self.height = height
        self.xdescent = xdescent
        self.ydescent = ydescent

        self.offset_transform = mtransforms.Affine2D()
        self.offset_transform.clear()
        self.offset_transform.translate(0, 0)


    def get_transform(self):
        """
        Return the :class:`~matplotlib.transforms.Transform` applied
        to the children
        """
        return self.offset_transform

    def set_transform(self, t):
        """
        set_transform is ignored.
        """
        pass


    def set_offset(self, xy):
        """
        set offset of the container.

        Accept : tuple of x,y cooridnate in disokay units.
        """
        self._offset = xy

        self.offset_transform.clear()
        self.offset_transform.translate(xy[0], xy[1])


    def get_offset(self):
        """
        return offset of the container.
        """
        return self._offset

        
    def get_window_extent(self, renderer):
        '''
        get the bounding box in display space.
        '''
        w, h, xd, yd = self.get_extent(renderer)
        ox, oy = self.get_offset() #w, h, xd, yd)
        return mtransforms.Bbox.from_bounds(ox-xd, oy-yd, w, h)


    def get_extent(self, renderer):
        """
        Return with, height, xdescent, ydescent of box
        """
        return self.width, self.height, self.xdescent, self.ydescent



    def add_artist(self, a):
        'Add any :class:`~matplotlib.artist.Artist` to the container box'
        self._children.append(a)
        a.set_transform(self.get_transform())


    def draw(self, renderer):
        """
        Draw the children
        """

        for c in self._children:
            c.draw(renderer)

        bbox_artist(self, renderer, fill=False, props=dict(pad=0.))


class TextArea(OffsetBox):
    """
    The TextArea is contains a single Text instance. The text is
    placed at (0,0) with baseline+left alignment. The width and height
    of the TextArea instance is the width and height of the its child
    text.
    """


    
    def __init__(self, s, textprops=None, **kw):
        """
        *s* : a string to be displayer.
        *trnaspose* : transformation matrrix 
        """
        if textprops is None:
            textprops = {}

        if not textprops.has_key("va"):
            textprops["va"]="baseline"

        self._text = mtext.Text(0, 0, s, **textprops)

        OffsetBox.__init__(self)

        self._children = [self._text]
        

        self.offset_transform = mtransforms.Affine2D()
        self.offset_transform.clear()
        self.offset_transform.translate(0, 0)
        self._text.set_transform(self.offset_transform)


    def set_transform(self, t):
        """
        set_transform is ignored.
        """
        pass


    def set_offset(self, xy):
        """
        set offset of the container.

        Accept : tuple of x,y cooridnate in disokay units.
        """
        self._offset = xy

        self.offset_transform.clear()
        self.offset_transform.translate(xy[0], xy[1])


    def get_offset(self):
        """
        return offset of the container.
        """
        return self._offset

        
    def get_window_extent(self, renderer):
        '''
        get the bounding box in display space.
        '''
        w, h, xd, yd = self.get_extent(renderer)
        ox, oy = self.get_offset() #w, h, xd, yd)
        return mtransforms.Bbox.from_bounds(ox-xd, oy-yd, w, h)


    def get_extent(self, renderer):
        ismath = self._text.is_math_text(self._text._text)
        _, h_, d_ = renderer.get_text_width_height_descent(
            "lp", self._text._fontproperties, ismath=False)

        bbox, info = self._text._get_layout(renderer)
        w, h = bbox.width, bbox.height
        line = info[0][0] # first line

        _, hh, dd = renderer.get_text_width_height_descent(
            line, self._text._fontproperties, ismath=ismath)
        d = h-(hh-dd)  # the baseline of the first line

        # for multiple lines, h or d may greater than h_ or d_.
        h_d = max(h_ - d_, h-d)
        d = max(d, d_)
        h = h_d + d

        return w, h, 0., d


    def draw(self, renderer):
        """
        Draw the children
        """

        self._text.draw(renderer)

        bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

