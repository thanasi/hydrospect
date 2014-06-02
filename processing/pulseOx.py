# since the data is quite smoothed to begin with (coming from the teensy), we do not need any smoothing functions
# we shall directly communicate with the teensy, and control the LEDs based on functions written on the teensy.
# data will be taken for a fixed period of time from the teensy after the LED is turned on, and then stopped.
# In that meantime it shall be processed and the numbers (pulseOx and heart rate) shall be thrown out.

