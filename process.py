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

import matplotlib, numpy

fileToRead = 'data.txt'		# later we will add a TkInter dialog box to select data files.
time, amplitude = numpy.loadtxt(fileToRead, skiprows=3, unpack=True)	# read in the file

# next we declare the holders for peaks
maximas = []
minimas = []
peakTIme = []	# stores the time at which a peak maxima happens (to get pulse)

'''
# now we start looping through all the lines of data till the last but one
for i in range(0, len(time) - 1):
  # we'll go ahead and split three rows into columns..
  prevVal = rawData[i-1].split()
  currentVal = rawData[i].split()
  nextVal = rawData[i+1].split()
  
  # thereafter, we put them into their designated variables
  # first the current time...
  time = currentVal[0]
  
  # then all the amplitudes...
  prevAmpl = prevVal[1]
  currentAmpl = currentVal[1]
  nextAmpl = nextVal[1]
  
  # at this point, we check the amplitude for a minima or a maxima...
  if (currentAmpl >= prevAmpl and currentAmpl >= nextAmpl):		# greater than the previous and next..
    # It's a maxima, captain!
    maximas.append(currentAmpl)
    peakTIme.append(time)
	
  if (currentAmpl <= prevAmpl and currentAmpl <= nextAmpl):
    # minima...
	minimas.append(currentAmpl)
	
print len(maximas)
'''