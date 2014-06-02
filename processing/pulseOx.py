# since the data is quite smoothed to begin with (coming from the teensy), we do not need any smoothing functions
# we shall directly communicate with the teensy, and control the LEDs based on functions written on the teensy.
# data will be taken for a fixed period of time from the teensy after the LED is turned on, and then stopped.
# In that meantime it shall be processed and the numbers (pulseOx and heart rate) shall be thrown out.

##### IMPORT STATEMENTS, VARIABLE DECLARATIONS..
import serial, numpy

# step1: open the serial port

teensy = serial.Serial(3, 115200)		# open serial port

# step 2: send the "begin the red colour" command...

# step 3: start acquiring data and storing it into a numpy array

# step 4: After a certain number of datapoints have been acquired, stop acqisition, send the "begin the IR colour" command...

# step 5: start acquiring data and storing it into a second variable/array

# step 6: PROCESSING begins. Find the peaks for both variables. Store into variable/array. Find the time difference between peaks, and store this into variables.

# step 7: find the logs of the ratios from the peaks.

# step 8: find the o2 sat value yo. spit it out.