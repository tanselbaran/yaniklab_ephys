from scipy import signal
import numpy as np

def lowpass_filter(rate=None, high=None, order=None):
    """Butterworth lowpass filter."""
    assert order >= 1
    return signal.butter(order,
                         (high / (rate / 2.)),
                         'lowpass')

def bandpass_filter(rate=None, high=None, low=None, order=None):
    """Butterworth bandpass filter."""
    assert order >= 1
    return signal.butter(order, [(low/(rate/2.)), (high/(rate/2.))], 'bandpass')

def notch_filter(rate=None, high=None, low=None, order=None):
    #Butterworth notch filter
    assert order >= 1
    return signal.butter(order, [(low/(rate/2.)), (high/(rate/2.))], 'bandstop')

def apply_filter(x, filter=None, axis=None):
    """Apply a filter to an array."""
    if isinstance(x, list):
        x = np.asarray(x)
    if x.shape[axis] == 0:
        return x
    b, a = filter
    return signal.filtfilt(b, a, x[:], axis=axis)

class Filter(object):
    """Multichannel filter.

    The filter is applied on every column of a 2D array.

    Example
    -------

    ```python
    fil = Filter(rate=20000., high=300., order=4)
    traces_f = fil(traces)
    ```

    """

    def __call__(self, data):
        return apply_filter(data, filter=self._filter, axis = self._axis)

class bandpassFilter(Filter):
    def __init__(self, rate=None, high=None, low=None, order=None, axis = None):
        self._filter = bandpass_filter(rate=rate, high=high, low=low, order=order)
        self._axis = axis

class notchFilter(Filter):
    def __init__(self, rate=None, high=None, low=None, order=None, axis = None):
        self._filter = notch_filter(rate=rate, high=high, low=low, order=order)
        self._axis = axis

class lowpassFilter(Filter):
    def __init__(self, rate=None, high=None, order=None, axis = None):
        self._filter = lowpass_filter(rate=rate, high=high, order=order)
        self._axis = axis
