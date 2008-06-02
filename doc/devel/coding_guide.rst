.. _coding-guide:

************
Coding Guide
************

.. _version-control:

Version Control
===============

svn checkouts
-------------

Checking out everything in the trunk (matplotlib and toolkits)::

   svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk \
   matplotlib --username=youruser --password=yourpass

Checking out the main source::

   svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/trunk/\
   matplotlib mpl --username=youruser --password=yourpass

Branch checkouts, eg the maintenance branch::

   svn co https://matplotlib.svn.sourceforge.net/svnroot/matplotlib/branches/\
   v0_91_maint mpl91 --username=youruser --password=yourpass

Committing changes
------------------

When committing changes to matplotlib, there are a few things to bear
in mind.

* if your changes are non-trivial, please make an entry in the
  :file:`CHANGELOG`
* if you change the API, please document it in :file:`API_CHANGES`, and
  consider posting to mpl-devel
* Are your changes python2.4 compatible?  We are still trying to
  support 2.4, so avoid features new to 2.5
* Can you pass :file:`examples/tests/backend_driver.py`?  This is our
  poor man's unit test.
* If you have altered extension code, do you pass
  :file:`unit/memleak_hawaii.py`?
* if you have added new files or directories, or reorganized existing
  ones, are the new files included in the match patterns in
  :file:`MANIFEST.in`.  This file determines what goes into the source
  distribution of the mpl build.
* Keep the maintenance branch and trunk in sync where it makes sense.
  If there is a bug on both that needs fixing, use `svnmerge.py
  <http://www.orcaware.com/svn/wiki/Svnmerge.py>`_ to keep them in
  sync.  The basic procedure is:

  * install ``svnmerge.py`` in your PATH::

      wget http://svn.collab.net/repos/svn/trunk/contrib/client-side/\
      svnmerge/svnmerge.py

  * get a svn copy of the maintenance branch and the trunk (see above)
  * Michael advises making the change on the branch and committing
    it.  Make sure you svn upped on the trunk and have no local
    modifications, and then from the svn trunk do::

       > svnmerge.py merge

    If you wish to merge only specific revisions (in an unusual
    situation), do::

       > svnmerge.py merge -rNNN1-NNN2

    where the ``NNN`` are the revision numbers.  Ranges are also
    acceptable.

    The merge may have found some conflicts (code that must be
    manually resolved).  Correct those conflicts, build matplotlib and
    test your choices.

    ``svnmerge.py`` automatically creates a file containing the commit
    messages, so you are ready to make the commit::

       > svn commit -F svnmerge-commit-message.txt


.. _style-guide:

Style Guide
===========

Importing and name spaces
-------------------------

For `numpy <http://www.numpy.org>`_, use::

  import numpy as np
  a = np.array([1,2,3])

For masked arrays, use::

  from numpy import ma

(The earlier recommendation, :samp:`import matplotlib.numerix.npyma as ma`,
was needed temporarily during the development of the maskedarray
implementation as a separate package.  As of numpy 1.1, it replaces the
old implementation. Note: ``from numpy import ma`` works with numpy < 1.1
*and* with numpy >= 1.1.  ``import numpy.ma as ma`` works *only* with
numpy >= 1.1, so for now we must not use it.)

For matplotlib main module, use::

  import matplotlib as mpl
  mpl.rcParams['xtick.major.pad'] = 6

For matplotlib modules (or any other modules), use::

  import matplotlib.cbook as cbook

  if cbook.iterable(z):
      pass

We prefer this over the equivalent ``from matplotlib import cbook``
because the latter is ambiguous whether ``cbook`` is a module or a
function to the new developer.  The former makes it explcit that
you are importing a module or package.

Naming, spacing, and formatting conventions
-------------------------------------------

In general, we want to hew as closely as possible to the standard
coding guidelines for python written by Guido in `PEP 0008
<http://www.python.org/dev/peps/pep-0008>`_, though we do not do this
throughout.

* functions and class methods: ``lower`` or
  ``lower_underscore_separated``

* attributes and variables: ``lower`` or ``lowerUpper``

* classes: ``Upper`` or ``MixedCase``

Personally, I prefer the shortest names that are still readable.

Also, use an editor that does not put tabs in files.  Four spaces
should be used for indentation everywhere and if there is a file with
tabs or more or less spaces it is a bug -- please fix it.

Please avoid spurious invisible spaces at the ends of lines.
(Tell your editor to strip whitespace from line ends when saving
a file.)

Keep docstrings uniformly indented as in the example below, with
nothing to the left of the triple quotes.  The
:func:`matplotlib.cbook.dedent` function is needed to remove excess
indentation only if something will be interpolated into the docstring,
again as in the example above.

Limit line length to 80 characters.  If a logical line needs to be
longer, use parentheses to break it; do not use an escaped newline.
It may be preferable to use a temporary variable to replace a single
long line with two shorter and more readable lines.

Please do not commit lines with trailing white space, as it causes
noise in svn diffs.

If you are an emacs user, the following in your ``.emacs`` will cause
emacs to strip trailing white space upon saving for python, C and C++:

.. code-block:: cl

  ; and similarly for c++-mode-hook and c-mode-hook
  (add-hook 'python-mode-hook
            (lambda ()
	    (add-hook 'write-file-functions 'delete-trailing-whitespace)))

for older versions of emacs (emacs<22) you need to do: 

.. code-block:: cl

  (add-hook 'python-mode-hook
            (lambda ()
            (add-hook 'local-write-file-hooks 'delete-trailing-whitespace)))

Keyword argument processing
---------------------------

Matplotlib makes extensive use of ``**kwargs`` for pass through
customizations from one function to another.  A typical example is in
:func:`matplotlib.pylab.text`.  The definition of the pylab text
function is a simple pass-through to
:meth:`matplotlib.axes.Axes.text`::

  # in pylab.py
  def text(*args, **kwargs):
      ret =  gca().text(*args, **kwargs)
      draw_if_interactive()
      return ret

:meth:`~matplotlib.axes.Axes.text` in simplified form looks like this,
i.e., it just passes them on to :meth:`matplotlib.text.Text.__init__`::

  # in axes.py
  def text(self, x, y, s, fontdict=None, withdash=False, **kwargs):
      t = Text(x=x, y=y, text=s, **kwargs)

and :meth:`~matplotlib.text.Text.__init__` (again with liberties for
illustration) just passes them on to the
:meth:`matplotlib.artist.Artist.update` method::

  # in text.py
  def __init__(self, x=0, y=0, text='', **kwargs):
      Artist.__init__(self)
      self.update(kwargs)

``update`` does the work looking for methods named like
``set_property`` if ``property`` is a keyword argument.  I.e., no one
looks at the keywords, they just get passed through the API to the
artist constructor which looks for suitably named methods and calls
them with the value.

As a general rule, the use of ``**kwargs`` should be reserved for
pass-through keyword arguments, as in the examaple above.  If I intend
for all the keyword args to be used in some function and not passed
on, I just use the key/value keyword args in the function definition
rather than the ``**kwargs`` idiom.

In some cases I want to consume some keys and pass through the others,
in which case I pop the ones I want to use locally and pass on the
rest, eg., I pop ``scalex`` and ``scaley`` in
:meth:`~matplotlib.axes.Axes.plot` and assume the rest are
:meth:`~matplotlib.lines.Line2D` keyword arguments.  As an example of
a pop, passthrough usage, see :meth:`~matplotlib.axes.Axes.plot`::

  # in axes.py
  def plot(self, *args, **kwargs):
      scalex = kwargs.pop('scalex', True)
      scaley = kwargs.pop('scaley', True)
      if not self._hold: self.cla()
      lines = []
      for line in self._get_lines(*args, **kwargs):
          self.add_line(line)
          lines.append(line)

The :mod:`matplotlib.cbook` function :func:`~matplotlib.cbook.popd` is rendered
obsolete by the :func:`~dict.pop` dictionary method introduced in Python 2.3,
so it should not be used for new code.

Note there is a use case when ``kwargs`` are meant to be used locally
in the function (not passed on), but you still need the ``**kwargs``
idiom.  That is when you want to use ``*args`` to allow variable
numbers of non-keyword args.  In this case, python will not allow you
to use named keyword args after the ``*args`` usage, so you will be
forced to use ``**kwargs``.  An example is
:meth:`matplotlib.contour.ContourLabeler.clabel`::

  # in contour.py
  def clabel(self, *args, **kwargs):
      fontsize = kwargs.get('fontsize', None)
      inline = kwargs.get('inline', 1)
      self.fmt = kwargs.get('fmt', '%1.3f')
      colors = kwargs.get('colors', None)
      if len(args) == 0:
          levels = self.levels
          indices = range(len(self.levels))
      elif len(args) == 1:
         ...etc...

.. _docstrings:

Documentation and Docstrings
============================

matplotlib uses artist instrospection of docstrings to support
properties.  All properties that you want to support through ``setp``
and ``getp`` should have a ``set_property`` and ``get_property``
method in the :class:`~matplotlib.artist.Artist` class.  Yes, this is
not ideal given python properties or enthought traits, but it is a
historical legacy for now.  The setter methods use the docstring with
the ACCEPTS token to indicate the type of argument the method accepts.
Eg. in :class:`matplotlib.lines.Line2D`::

  # in lines.py
  def set_linestyle(self, linestyle):
      """
      Set the linestyle of the line

      ACCEPTS: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ]
      """

Since matplotlib uses a lot of pass through ``kwargs``, eg. in every
function that creates a line (:func:`~matplotlib.pyplot.plot`,
:func:`~matplotlib.pyplot.semilogx`,
:func:`~matplotlib.pyplot.semilogy`, etc...), it can be difficult for
the new user to know which ``kwargs`` are supported.  I have developed a
docstring interpolation scheme to support documentation of every
function that takes a ``**kwargs``.  The requirements are:

1. single point of configuration so changes to the properties don't
   require multiple docstring edits.

2. as automated as possible so that as properties change the docs
   are updated automagically.

I have added a :attr:`matplotlib.artist.kwdocd` and
:func:`matplotlib.artist.kwdoc` to faciliate this.  They combine
python string interpolation in the docstring with the matplotlib
artist introspection facility that underlies ``setp`` and ``getp``.  The
``kwdocd`` is a single dictionary that maps class name to a docstring of
``kwargs``.  Here is an example from :mod:`matplotlib.lines`::

  # in lines.py
  artist.kwdocd['Line2D'] = artist.kwdoc(Line2D)

Then in any function accepting :class:`~matplotlib.lines.Line2D`
passthrough ``kwargs``, eg. :meth:`matplotlib.axes.Axes.plot`::

  # in axes.py
  def plot(self, *args, **kwargs):
      """
      Some stuff omitted

      The kwargs are Line2D properties:
      %(Line2D)s

      kwargs scalex and scaley, if defined, are passed on
      to autoscale_view to determine whether the x and y axes are
      autoscaled; default True.  See Axes.autoscale_view for more
      information
      """
      pass
  plot.__doc__ = cbook.dedent(plot.__doc__) % artist.kwdocd

Note there is a problem for :class:`~matplotlib.artist.Artist`
``__init__`` methods, eg. :meth:`matplotlib.patches.Patch.__init__`,
which supports ``Patch`` ``kwargs``, since the artist inspector cannot work
until the class is fully defined and we can't modify the
``Patch.__init__.__doc__`` docstring outside the class definition.  I have
made some manual hacks in this case which violates the "single entry
point" requirement above; hopefully we'll find a more elegant solution
before too long.


.. _licenses:

Licenses
========

Matplotlib only uses BSD compatible code.  If you bring in code from
another project make sure it has a PSF, BSD, MIT or compatible
license.  If not, you may consider contacting the author and asking
them to relicense it.  GPL and LGPL code are not acceptible in the
main code base, though we are considering an alternative way of
distributing L/GPL code through an separate channel, possibly a
toolkit.  If you include code, make sure you include a copy of that
code's license in the license directory if the code's license requires
you to distribute the license with it.