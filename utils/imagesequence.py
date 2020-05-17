"""
A system for managing a controlled sequence of image frames.
"""
import time
import re
import ppb

FILE_PATTERN = re.compile(r'\{(\d+)\.\.(\d+)\}')


class Sequence:
    """
    An "image" that represents a sequence of image frames that can be moved back and forth
    to select a correct frame at any given time.
    """

    clock = time.perf_counter

    def __init__(self, filename):
        """
        :param str filename: A path containing a ``{2..4}`` indicating the frame number
        """
        self._filename = filename
        self._frames = []
        self._frame_index = None

        self._offset = -self._clock()
        self._compile_filename()

    def __repr__(self):
        return f"{type(self).__name__}({self._filename!r})"

    # Do we need pickle/copy dunders?
    def copy(self):
        """
        Create a new Sequence with the same filename pattern. Pause
        status and starting time are reset.
        """
        return type(self)(self._filename)
    
    def prev(self):
        self._frame_index = self._frame_index - 1
        if self._frame_index < 0:
            self._frame_index = len(self._frames) - 1

    def next(self):
        self._frame_index = (self._frame_index + 1) % len(self._frames)
    
    def set_ratio(self, value):
        if value == 0.0:
            self._frame_index = 0
        if value == 1.0:
            self._frame_index = len(self._frames) - 1
        else:
            self._frame_index = int(value * len(self._frames))

    def _clock(self):
        return self.clock()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
        self._compile_filename()

    def _compile_filename(self):
        match = FILE_PATTERN.search(self._filename)
        start, end = match.groups()
        numdigits = max(len(start), len(end))
        start = int(start)
        end = int(end)
        template = FILE_PATTERN.sub(
            '{:0%dd}' % numdigits,
            self._filename,
        )
        self._frames = [
            ppb.Image(template.format(n))
            for n in range(start, end + 1)
        ]
        if self._frames:
            self._frame_index = 0
        else:
            self._frame_index = None

    @property
    def current_frame(self):
        if self._frames:
            try:
                return self._frames[self._frame_index]
            except IndexError:
                return self._frames[0]
        else:
            return None

    def load(self):
        """
        Get the current frame path.
        """
        frame = self.current_frame
        return frame.load() if frame else None

    # This is so that if you assign an Animation to a class, instances will get
    # their own copy, so their animations run independently.
    _prop_name = None

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        v = vars(obj)
        if self._prop_name not in v:
            v[self._prop_name] = self.copy()
        return v[self._prop_name]

    # Don't need __set__() or __delete__(), additional accesses will be via
    # __dict__ directly.

    def __set_name__(self, owner, name):
        self._prop_name = name