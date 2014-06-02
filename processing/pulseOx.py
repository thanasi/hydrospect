# since the data is quite smoothed to begin with (coming from the teensy), we do not need any smoothing functions
# we shall directly communicate with the teensy, and control the LEDs based on functions written on the teensy.
# data will be taken for a fixed period of time from the teensy after the LED is turned on, and then stopped.
# In that meantime it shall be processed and the numbers (pulseOx and heart rate) shall be thrown out.

##### IMPORT STATEMENTS, VARIABLE DECLARATIONS..
import serial, numpy, time
serialData = []

# step1: open the serial port
print("opening port..")
teensy = serial.Serial(3, 115200, timeout=1)		# open serial port, needs to be one less than what Arduino IDE shows (COMx)

# step 2: send the "begin the red colour" command...
print("red led..")
teensy.write('r')	# the red light's on and the data's being captured into a local variable on the teensy
print ("collecting data from red led... please wait 5 seconds...")
time.sleep(6)		# wait 6 seconds, let the data be collected for a 5 second interval and don't do anything till then
	
# step 3: after 5 seconds are up, put the lights off and disable the timer interrupt on the teensy
teensy.write('q')	# put the lights off

# step 4: Send the "begin the IR colour" command...
print("IR led")
teensy.write('i')	# start IR light and acquisition
print("collecting data from IR led, please wait...")
time.sleep(6)

# step 5: start acquiring data and storing it into a variable/array, then close serial port.
print("now will begin the transmission of data from arduino to python over serial...")
teensy.write('t')
for i in  range(0,1000):
  data = teensy.readline()
  serialData.extend(data)
  print(str(i) + ": " + data)

print("data collection done!")
teensy.close()
# step 6: PROCESSING begins. Find the peaks for both variables. Store into variable/array. Find the time difference between peaks, and store this into variables.


# step 7: find the logs of the ratios from the peaks.

# step 8: find the o2 sat value yo. spit it out.