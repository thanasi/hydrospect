# since the data is quite smoothed to begin with (coming from the teensy), we do not need any smoothing functions
# we shall directly communicate with the teensy, and control the LEDs based on functions written on the teensy.
# data will be taken for a fixed period of time from the teensy after the LED is turned on, and then stopped.
# In that meantime it shall be processed and the numbers (pulseOx and heart rate) shall be thrown out.

##### IMPORT STATEMENTS, VARIABLE DECLARATIONS..
import serial, numpy, scipy.signal, time
import matplotlib.pyplot as plt

serialData = []
redData = []
redMaximas = []
irData = []
irMaximas = []
redMinimas = []
irMinimas = []
# the time axis, specified from before...
t = numpy.arange(0,5,0.005)

### function definitions...
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

# step1: open the serial port
print("opening port..")
teensy = serial.Serial(3, 115200, timeout=1)		# open serial port, needs to be one less than what Arduino IDE shows (COMx)

# step 2: send the "begin the red colour" command...
print("red led..")
time.sleep(1)
teensy.write('r')	# the red light's on and the data's being captured into a local variable on the teensy
print ("collecting data from red led... please wait 5 seconds...")
time.sleep(6)		# wait 6 seconds, let the data be collected for a 5 second interval and don't do anything till then
	
# step 3: after 5 seconds are up, put the lights off and disable the timer interrupt on the teensy
teensy.write('q')	# put the lights off

# step 4: Send the "begin the IR colour" command...
print("IR led")
teensy.write('i')	# start IR light and acquisition
time.sleep(1)
print("collecting data from IR led, please wait...")
time.sleep(6)

# step 5: start acquiring data and storing it into a variable/array, then close serial port.
print("now will begin the transmission of data from arduino to python over serial...")
teensy.write('t')
for i in  range(0,1000):
  data = teensy.readline()
  serialData.append(data)
  # print(str(i) + ": " + data)

print("data collection done!")
teensy.close()

### then we go ahead and split the data at our leisure
for j in range(0,1000):
  z = ((serialData[j]).strip()).split('\t')		# split data at tab
  # print(z)
  red = int(z[0])
  # print red
  
  ir = int(z[1])
  redData.append(red)			# append int version of the value into the datas list
  irData.append(ir)

### we then need to convert these lists to numpy arrays in order for them to be used by scipy
redData = numpy.array(redData)
irData = numpy.array(irData)

# we're also going to smooth these before making them numpy arrays.
smoothWindow = 21		# make sure this is always an odd number
plotCutoffs = int(smoothWindow/2)
redDataSmoothed = smooth(numpy.array(redData), window_len=smoothWindow)[plotCutoffs:-plotCutoffs]
irDataSmoothed = smooth(numpy.array(irData), window_len=smoothWindow)[plotCutoffs:-plotCutoffs]

# step 6: PROCESSING begins. Find the peaks for both variables. Store into variable/array. Find the time difference between peaks, and store this into variables.
# REMEMBER THAT THE DATA IS int COMING FROM THE ADC
# also remember that argrelextrema returns the indices of the extremas, not the extremas themselves
### finding the maximas...
argrelOrder = 30				# set the order/window for maxima/minima peak finding
redMaximas = scipy.signal.argrelmax(redDataSmoothed, order=argrelOrder)
irMaximas = scipy.signal.argrelmax(irDataSmoothed, order=argrelOrder)

### finding the minimas...
redMinimas = scipy.signal.argrelmin(redDataSmoothed, order=argrelOrder)
irMinimas = scipy.signal.argrelmin(irDataSmoothed, order=argrelOrder)

### printing out the maximas and minimas to test...
'''
print redMinimas
print redMaximas
print irMinimas
print irMaximas
'''

### will find the pulse now, as the test...
averager = 0
for k in range(0, len(redMaximas[0])-2):
  pulse = 60/((redMaximas[0][k+1]-redMaximas[0][k])*0.005)
  averager += pulse
  
print "here's your pulse: "
print averager/len(redMaximas[0])
  
  
### we shall now plot them...
plt.plot(t, redData, 'k--', t, irData, 'b--')
plt.plot(t, redDataSmoothed, 'r', t, irDataSmoothed, 'g')
plt.plot(t[redMaximas[0]], redData[redMaximas[0]], 'ko')
plt.plot(t[redMinimas[0]], redData[redMinimas[0]], 'bo')
plt.plot(t[irMaximas[0]], irData[irMaximas[0]], 'ko')
plt.plot(t[irMinimas[0]], irData[irMinimas[0]], 'bo')
plt.show()

# step 7: find the logs of the ratios from the peaks.

# step 8: find the o2 sat value yo. spit it out.