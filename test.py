import gpio_interface
import time

gpio_interface.onSignal()
time.sleep(5)
gpio_interface.offSignal()

