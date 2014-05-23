# 18-MAY-2014 DJ started work on this file
# We will read tab-delimited txt files from the oscilloscope into a voltage-time data set. 
# First we need to low-pass filter this baby. Then we plot the pre-and post-filtered.
# Local peaks will be found, grouped into 'maxima' and 'minima', which correspond to AC/DC values. THe pulse will be found and thrown into an averager and the ratio of these peaks too which be thrown into an averager.
# The log of the ratio will be taken
# This log will then be used in a good ol' 3x3 matrix system of linear equations and will then be solved for the concentrations.
# Here, the epsilons will be entered as variables RIGHT at the start so that they can be edited as required (and the inverse found each time on-the-fly

# THe smoothing functions that is being used.. 
# the first 'smooth' is taken from http://wiki.scipy.org/Cookbook/SignalSmooth
# skip this function to see the main code...
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

# the next one models a savitzky-golay smoothening, taken from https://gist.github.com/RyanHope/2321077
def savitzky_golay( y, window_size, order, deriv = 0 ):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techhniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = numpy.linspace(-4, 4, 500)
    y = numpy.exp( -t**2 ) + numpy.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, numpy.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    try:
        window_size = numpy.abs( numpy.int( window_size ) )
        order = numpy.abs( numpy.int( order ) )
    except ValueError, msg:
        raise ValueError( "window_size and order have to be of type int" )
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError( "window_size size must be a positive odd number" )
    if window_size < order + 2:
        raise TypeError( "window_size is too small for the polynomials order" )
    order_range = range( order + 1 )
    half_window = ( window_size - 1 ) // 2
    # precompute coefficients
    b = numpy.mat( [[k ** i for i in order_range] for k in range( -half_window, half_window + 1 )] )
    m = numpy.linalg.pinv( b ).A[deriv]
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - numpy.abs( y[1:half_window + 1][::-1] - y[0] )
    lastvals = y[-1] + numpy.abs( y[-half_window - 1:-1][::-1] - y[-1] )
    y = numpy.concatenate( ( firstvals, y, lastvals ) )
    return numpy.convolve( m, y, mode = 'valid' )

# there are three epsilon arrays, and they in turn shall have 3 members,
# the exctinction coefficients at 630, 850, 950 respectively.
epsilon_Hb = []
epsilon_HbO2 = []
epsilon_H2O = []

import matplotlib.pyplot as plt, numpy, scipy.signal

time = []
amplitude = []
for i in range(1,7):
  fileToRead = 'data/20140522/630nm/20140522-0002/20140522-0002_' + str(i) + '.txt'		# later we will add a TkInter dialog box to select data files.
  parttime, partamplitude = numpy.loadtxt(fileToRead, skiprows=3, unpack=True)	# read in the file
  # we need to increment the parttime variable with the previous last item, since the oscilloscope seems to have divided the sections up without preserving the totality of time
  # here we are assuming that all the data chunks are of the exact same time duration and sampling, which is true
  parttime += (i-1)*10.00059975
  time += parttime.tolist()			# need to convert array to list to be able to concatenate like a list
  amplitude += partamplitude.tolist()
  print i, parttime[0]

# next we declare the holders for peaks
maximas = []
minimas = []
peakTIme = []	# stores the time at which a peak maxima happens (to get pulse)

# next we shall go about band-pass filtering the data and displaying it to see that it is to our satisfaction
# we start by finding the upper and lower frequency bounds of this data...
fs = 1/(time[1]-time[0])	# sampling rate
fnyq = fs/2					# nyquist frequency

# print "sampling frequency =", fs
# print "lowest frequency =", 1/(time[-1]-time[0])

# knowing these, we can start experimenting with a bandpass filter that would be most to our satisfaction..
# variables relating to the filter:
fCutoffHigh = 43	# Hz
fCutoffLow = 0.5	# Hz
butterOrder = 1

# filter definition... we start with the lowpass filter
# b, a = scipy.signal.butter(butterOrder, [fCutoffLow/fnyq, fCutoffHigh/fnyq], btype='band', analog=True)
b, a = scipy.signal.butter(butterOrder, [fCutoffHigh/fnyq])

# next we apply the filter on the 'amplitude' variable (which is the data)
filteredAmpl = scipy.signal.lfilter(b, a, amplitude)

# then we totally smooth the shit out of the filtered signal
smoothingOrder = 501		# this needs to be subtracted later from the smoothed array
# smoothedAmpl = smooth(filteredAmpl, filteredAmpl)			# using the dual-window smoothing function
smoothedAmpl = savitzky_golay(filteredAmpl, window_size=551, order=4)								# Savitzky-Golay filter

# Right. After this we bandpass it, while letter DC go through but not allowing a low-freqyency region between 0 and 0.5Hz to go through
# b,a = scipy.signal.butter(1, [0.1/fnyq, 0.5/fnyq], btype='bandstop')
# b = scipy.signal.firwin(2, cutoff=0.1, nyq=fnyq, pass_zero=True)
# lowFreqRemovedAmpl = scipy.signal.lfilter(b, a, filteredAmpl)

# we then plot these w.r.t. time
plt.figure(1)
plt.clf
plt.autoscale(enable=True, axis='both', tight=True)
plt.plot(time, amplitude, 'g', label='Original signal (Hz)')		# original, green
plt.plot(time, filteredAmpl, 'b', label='Filtered signal (Hz)')		# filtered
# plt.plot(time, smoothedAmpl[(smoothingOrder/2)-1:-(smoothingOrder/2)-1], 'k', label='Filtered signal (Hz)')		# smoothed, black colour 'k' and phase-adjusted to match the main signals
plt.plot(time, smoothedAmpl, 'k', label='Savitzky-Golay smoothed')
# plt.plot(time, lowFreqRemovedAmpl, 'r', label='Leveled signal (Hz)')

plt.xlabel('time (seconds)')
plt.grid(True)
plt.legend(loc='upper left')

plt.show()

# next what we want to do is to be able to remove the low-freqyency feature