.. _installing-faq:

*****************
 Installation FAQ
*****************


.. contents::
   :backlinks: none


Report a compilation problem
======================================

See :ref:`reporting-problems`.

matplotlib compiled fine, but nothing shows up with plot
==========================================================

The first thing to try is a :ref:`clean install <clean-install>` and see if
that helps.  If not, the best way to test your install is by running a script,
rather than working interactively from a python shell or an integrated
development environment such as :program:`IDLE` which add additional
complexities. Open up a UNIX shell or a DOS command prompt and cd into a
directory containing a minimal example in a file. Something like
:file:`simple_plot.py`, or for example::

  from pylab import *
  plot([1,2,3])
  show()

and run it with::

  python simple_plot.py --verbose-helpful

This will give you additional information about which backends matplotlib is
loading, version information, and more. At this point you might want to make
sure you understand matplotlib's :ref:`configuration <customizing-matplotlib>`
process, governed by the :file:`matplotlibrc` configuration file which contains
instructions within and the concept of the matplotlib backend.

If you are still having trouble, see :ref:`reporting-problems`.

.. _clean-install:

Cleanly rebuild and reinstall everything
==================================================

The steps depend on your platform and installation method.

Easy Install
------------

1. Delete the caches from your :ref:`.matplotlib configuration directory
   <locating-matplotlib-config-dir>`.

2. Run::

     easy_install -m PackageName


3. Delete any .egg files or directories from your :ref:`installation
   directory <locating-matplotlib-install>`.



Windows installer
-----------------

1. Delete the caches from your :ref:`.matplotlib configuration directory
   <locating-matplotlib-config-dir>`.

2. Use :menuselection:`Start --> Control Panel` to start the :program:`Add and
   Remove Software` utility.

Source install
--------------

Unfortunately::

    python setup.py clean

does not properly clean the build directory, and does nothing to the
install directory.  To cleanly rebuild:

1. Delete the caches from your :ref:`.matplotlib configuration directory
   <locating-matplotlib-config-dir>`.

2. Delete the ``build`` directory in the source tree

3. Delete any matplotlib directories or eggs from your `installation directory
   <locating-matplotlib-install>`


.. _install-svn:

Install from svn
========================

Checking out the main source::

   svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/matplotlib matplotlib

and build and install as usual with::

  > cd matplotlib
  > python setup.py install

Install from git
================

There is an experimental `matplotlib github mirror`_ of the subversion
repository. To make a local clone of it in the directory ``mpl.git``,
enter the following commands::

  # This will create your copy in the mpl.git directory             
  git clone git://github.com/astraw/matplotlib.git mpl.git
  cd mpl.git
  git config --add remote.origin.fetch +refs/remotes/*:refs/remotes/*
  git fetch
  git svn init --trunk=trunk/matplotlib --tags=tags https://matplotlib.svn.sourceforge.net/svnroot/matplotlib

  # Now just get the latest svn revisions from the SourceForge SVN repository
  git svn fetch -r 6300:HEAD

.. _matplotlib github mirror: http://github.com/astraw/matplotlib

To install from this cloned repository, use the commands in the
:ref:`svn installation <install-svn>` section.

To update your git repository with the latest svn updates from SourceForge::

  git svn rebase

To list what changes will be committed to svn::

  git svn dcommit -n

To commit your changes to svn::

  git svn dcommit 

A note about git write access
-----------------------------

The matplotlib developers need to figure out if there should be write
access to the git repository. This implies using the personal URL
(``git@github.com:astraw/matplotlib.git``) rather than the public URL
(``git://github.com/astraw/matplotlib.git``) for the
repository. However, doing so may make life complicated in the sense
that then there are two writeable matplotlib repositories, which must
be synced to prevent divergence. This is probably not an
insurmountable problem, but it is a problem that the developers should
reach a consensus about. Watch this space...

Backends
========

.. _what-is-a-backend:

What is a backend?
------------------

A lot of documentation on the website and in the mailing lists refers
to the "backend" and many new users are confused by this term.
matplotlib targets many different use cases and output formats.  Some
people use matplotlib interactively from the python shell and have
plotting windows pop up when they type commands.  Some people embed
matplotlib into graphical user interfaces like wxpython or pygtk to
build rich applications.  Others use matplotlib in batch scripts to
generate postscript images from some numerical simulations, and still
others in web application servers to dynamically serve up graphs.

To support all of these use cases, matplotlib can target different
outputs, and each of these capabililities is called a backend (the
"frontend" is the user facing code, ie the plotting code, whereas the
"backend" does all the dirty work behind the scenes to make the
figure.  There are two types of backends: user interface backends (for
use in pygtk, wxpython, tkinter, qt or fltk) and hardcopy backends to
make image files (PNG, SVG, PDF, PS).

There are a two primary ways to configure your backend.  One is to set
the ``backend`` parameter in you ``matplotlibrc`` file (see
:ref:`customizing-matplotlib`)::

    backend : WXAgg   # use wxpython with antigrain (agg) rendering

The other is to use the matplotlib :func:`~matplotlib.use` directive::

    import matplotlib
    matplotlib.use('PS')   # generate postscript output by default

If you use the ``use`` directive, this must be done before importing
:mod:`matplotlib.pyplot` or :mod:`matplotlib.pylab`.

If you are unsure what to do, and just want to get cranking, just set
your backend to ``TkAgg``.  This will do the right thing for 95% of the
users.  It gives you the option of running your scripts in batch or
working interactively from the python shell, with the least amount of
hassles, and is smart enough to do the right thing when you ask for
postscript, or pdf, or other image formats.

If however, you want to write graphical user interfaces, or a web
application server (:ref:`howto-webapp`), or need a better
understanding of what is going on, read on. To make things a little
more customizable for graphical user interfaces, matplotlib separates
the concept of the renderer (the thing that actually does the drawing)
from the canvas (the place where the drawing goes).  The canonical
renderer for user interfaces is ``Agg`` which uses the `antigrain
<http://antigrain.html>`_ C++ library to make a raster (pixel) image
of the figure.  All of the user interfaces can be used with agg
rendering, eg ``WXAgg``, ``GTKAgg``, ``QTAgg``, ``TkAgg``.  In
addition, some of the user interfaces support other rendering engines.
For example, with GTK, you can also select GDK rendering (backend
``GTK``) or Cairo rendering (backend ``GTKCairo``).

For the rendering engines, one can also distinguish between `vector
<http://en.wikipedia.org/wiki/Vector_graphics>`_ or `raster
<http://en.wikipedia.org/wiki/Raster_graphics>`_ renderers.  Vector
graphics languages issue drawing commands like "draw a line from this
point to this point" and hence are scale free, and raster backends
generate a pixel represenation of the line whose accuracy depends on a
DPI setting.

Here is a summary of the matplotlib renderers (there is an eponymous
backed for each):

=============   ============   ================================================
Renderer        Filetypes      Description
=============   ============   ================================================
:term:`AGG`     :term:`png`    :term:`raster graphics` -- high quality images
                               using the `Anti-Grain Geometry`_ engine
PS              :term:`ps`     :term:`vector graphics` -- Postscript_ output
                :term:`eps`
PDF		:term:`pdf`    :term:`vector graphics` --
                               `Portable Document Format`_
SVG             :term:`svg`    :term:`vector graphics` --
                               `Scalable Vector Graphics`_
:term:`Cairo`   :term:`png`    :term:`vector graphics` --
                :term:`ps`     `Cairo graphics`_
	        :term:`pdf`
	        :term:`svg`
	        ...
:term:`GDK`     :term:`png`    :term:`raster graphics` --
                :term:`jpg`    the `Gimp Drawing Kit`_
	        :term:`tiff`
	        ...
=============   ============   ================================================

And here are the user interfaces and renderer combinations supported:

============   ================================================================
Backend        Description
============   ================================================================
GTKAgg         Agg rendering to a :term:`GTK` canvas (requires PyGTK_)
GTK            GDK rendering to a :term:`GTK` canvas (not recommended)
               (requires PyGTK_)
GTKCairo       Cairo rendering to a :term:`GTK` Canvas (requires PyGTK_)
WXAgg          Agg rendering to to a :term:`wxWidgets` canvas
               (requires wxPython_)
WX             Native :term:`wxWidgets` drawing to a :term:`wxWidgets` Canvas
               (not recommended) (requires wxPython_)
TkAgg          Agg rendering to a :term:`Tk` canvas (requires TkInter_)
QtAgg          Agg rendering to a :term:`Qt` canvas (requires PyQt_)
Qt4Agg         Agg rendering to a :term:`Qt4` canvas (requires PyQt4_)
FLTKAgg        Agg rendering to a :term:`FLTK` canvas (requires pyFLTK_)
============   ================================================================

.. _`Anti-Grain Geometry`: http://www.antigrain.com/
.. _Postscript: http://en.wikipedia.org/wiki/PostScript
.. _`Portable Document Format`: http://en.wikipedia.org/wiki/Portable_Document_Format
.. _`Scalable Vector Graphics`: http://en.wikipedia.org/wiki/Scalable_Vector_Graphics
.. _`Cairo graphics`: http://en.wikipedia.org/wiki/Cairo_(graphics)
.. _`Gimp Drawing Kit`: http://en.wikipedia.org/wiki/GDK
.. _PyGTK: http://www.pygtk.org
.. _wxPython: http://www.wxpython.org/
.. _TkInter: http://wiki.python.org/moin/TkInter
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/intro
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/intro
.. _pyFLTK: http://pyfltk.sourceforge.net


.. _pygtk-2.4:

Compile matplotlib with PyGTK-2.4
-------------------------------------------

There is a `bug in PyGTK-2.4`_. You need to edit
:file:`pygobject.h` to add the :cmacro:`G_BEGIN_DECLS` and :cmacro:`G_END_DECLS`
macros, and rename :cdata:`typename` parameter to :cdata:`typename_`::

  -			  const char *typename,
  +			  const char *typename_,

.. _`bug in PyGTK-2.4`: http://bugzilla.gnome.org/show_bug.cgi?id=155304


OS-X questions
==============

.. _which-python-for-osx:

Which python for OS X?
----------------------

Apple ships with its own python, many users have had trouble
with it so there are alternatives.  If it is feasible for you, we
recommend the enthought python distribution `EPD
<http://www.enthought.com/products/epd.php>`_ for OS X (which comes
with matplotlib and much more) or the
`MacPython <http://wiki.python.org/moin/MacPython/Leopard>`_ or the
official OS X version from `python.org
<http://www.python.org/download/>`_.


.. _easy-install-osx-egg:

easy_install from egg?
------------------------------

Some users have reported problems with the egg for 0.98 from the
matplotlib download site, with ``easy_install``, getting an error::

    > easy_install ./matplotlib-0.98.0-py2.5-macosx-10.3-fat.egg
    Processing matplotlib-0.98.0-py2.5-macosx-10.3-fat.egg
    removing '/Library/Python/2.5/site-packages/matplotlib-0.98.0-py2.5-
    ...snip...
    Reading http://matplotlib.sourceforge.net
    Reading http://cheeseshop.python.org/pypi/matplotlib/0.91.3
    No local packages or download links found for matplotlib==0.98.0
    error: Could not find suitable distribution for
    Requirement.parse('matplotlib==0.98.0')

If you rename ``matplotlib-0.98.0-py2.5-macosx-10.3-fat.egg`` to
``matplotlib-0.98.0-py2.5.egg``, ``easy_install`` will install it from
the disk.  Many Mac OS X eggs with cruft at the end of the filename,
which prevents their installation through easy_install.  Renaming is
all it takes to install them; still, it's annoying.

Windows questions
=================

.. _windows-installers:

Binary installers for windows
----------------------------------------------

If you have already installed python, you can use one of the
matplotlib binary installers for windows -- you can get these from the
`sourceforge download
<http://sourceforge.net/project/platformdownload.php?group_id=80706>`_
site.  Choose the files that match your version of python (eg
``py2.5`` if you installed Python 2.5) which have the ``exe``
extension.  If you haven't already installed python, you can get the
official version from the `python web site
<http://python.org/download/>`_.  There are also two packaged
distributions of python that come preloaded with matplotlib and many
other tools like ipython, numpy, scipy, vtk and user interface
toolkits.  These packages are quite large because they come with so
much, but you get everything with a single click installer.

* the enthought python distribution `EPD
  <http://www.enthought.com/products/epd.php>`_

* `python (x, y) <http://www.pythonxy.com/foreword.php>`_
