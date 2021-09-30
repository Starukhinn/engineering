import RPi.GPIO as GPIO
import time
import math

dac = [26, 19, 13, 6, 5, 11, 9, 10]
bits = len(dac)
levels = 2 ** bits
max_voltage = 3.3
leds = [21, 20, 16, 12, 7, 8, 25, 24]
troyka = 17
comparator = 4

def decimal_to_binary(number):
    return [int(i) for i in bin(number)[2:].zfill(len(dac))]

def bin_to_dac(value):
    signal = decimal_to_binary(value)
    GPIO.output(dac, signal)
    return signal

def adc():
    for value in range(256):  
        time.sleep(0.0007)          
        signal = bin_to_dac(value)
        voltage = value / levels * max_voltage
        comparator_value = GPIO.input(comparator)
        if comparator_value == 0:
            print('ADC value = {:^3} -> {}, output voltage = {:.2f}'.format(value, signal, voltage))
            break

def adc_modified():
    value = 128
    add = 128
    while add >= 1:
        add = int(add/2)
        signal = bin_to_dac(value)
        voltage = value / levels * max_voltage
        time.sleep(0.001)
        comparator_value = GPIO.input(comparator)
        if comparator_value == 1:
            value += add
        elif comparator_value == 0:
            value -= add
    print('ADC value = {:^3} -> {}, output voltage = {:.2f}'.format(value, signal, voltage))


GPIO.setmode(GPIO.BCM)
GPIO.setup(dac, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(troyka, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(comparator, GPIO.IN)
GPIO.setup(leds, GPIO.OUT)

try:
    while True:
        adc_modified()

except KeyboardInterrupt:
    print('The program was stopped by the keyboatd')
else:
    print('No exceptions')
finally:
    GPIO.output(dac, GPIO.LOW)
    GPIO.output(leds, GPIO.LOW)
    GPIO.cleanup(dac)
    print('Cleanup completed')
    