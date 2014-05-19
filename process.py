# 18-MAY-2014 DJ started work on this file
# We will read tab-delimited txt files from the oscilloscope into a voltage-time data set. 
# First we need to low-pass filter this baby. Then we plot the pre-and post-filtered.
# Local peaks will be found, grouped into 'maxima' and 'minima', which correspond to AC/DC values. THe pulse will be found and thrown into an averager and the ratio of these peaks too which be thrown into an averager.
# The log of the ratio will be taken
# This log will then be used in a good ol' 3x3 matrix system of linear equations and will then be solved for the concentrations.
# Here, the epsilons will be entered as variables RIGHT at the start so that they can be edited as required (and the inverse found each time on-the-fly

# THe smoothing function that is being used.. taken from http://wiki.scipy.org/Cookbook/SignalSmooth
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

# there are three epsilon arrays, and they in turn shall have 3 members,
# the exctinction coefficients at 630, 850, 950 respectively.
epsilon_Hb = []
epsilon_HbO2 = []
epsilon_H2O = []

import matplotlib.pyplot as plt, numpy, scipy.signal

fileToRead = 'data.txt'		# later we will add a TkInter dialog box to select data files.
time, amplitude = numpy.loadtxt(fileToRead, skiprows=3, unpack=True)	# read in the file

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
smoothedAmpl = smooth(filteredAmpl, smoothingOrder)
print len(smoothedAmpl)
print len(time)

# we then plot these two w.r.t. time
plt.figure(1)
plt.clf
plt.autoscale(enable=True, axis='both', tight=True)
plt.plot(time, amplitude, 'g', label='Original signal (Hz)')		# original, green
plt.plot(time, filteredAmpl, 'b', label='Filtered signal (Hz)')		# filtered
plt.plot(time, smoothedAmpl[(smoothingOrder/2)-1:-(smoothingOrder/2)-1], 'k', label='Filtered signal (Hz)')		# smoothed, black colour 'k' and phase-adjusted to match the main signals

plt.xlabel('time (seconds)')
plt.grid(True)
plt.legend(loc='upper left')

plt.show()
