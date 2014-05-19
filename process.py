# 18-MAY-2014 DJ started work on this file
# We will read tab-delimited txt files from the oscilloscope into a voltage-time data set. 
# First we need to low-pass filter this baby. Then we plot the pre-and post-filtered.
# Local peaks will be found, grouped into 'maxima' and 'minima', which correspond to AC/DC values. THe pulse will be found and thrown into an averager and the ratio of these peaks too which be thrown into an averager.
# The log of the ratio will be taken
# This log will then be used in a good ol' 3x3 matrix system of linear equations and will then be solved for the concentrations.
# Here, the epsilons will be entered as variables RIGHT at the start so that they can be edited as required (and the inverse found each time on-the-fly

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
fCutoffHigh = 100	# Hz
fCutoffLow = 0.5	# Hz
butterOrder = 1

# filter definition...
# b, a = scipy.signal.butter(butterOrder, [fCutoffLow/fnyq, fCutoffHigh/fnyq], btype='band', analog=True)
b, a = scipy.signal.butter(butterOrder, [fCutoffHigh/fnyq])

# next we apply the filter on the 'amplitude' variable (which is the data)
filteredAmpl = scipy.signal.lfilter(b, a, amplitude)

# we then plot these two w.r.t. time
plt.figure(1)
plt.clf
plt.plot(time, amplitude, label='Original signal (Hz)')		# original
plt.plot(time, filteredAmpl, label='Filtered signal (Hz)')	# filtered
plt.xlabel('time (seconds)')
plt.grid(True)
plt.axis('tight')
plt.legend(loc='upper left')
plt.show()