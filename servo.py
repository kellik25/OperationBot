from machine import PWM, Pin
import time

class PositionServo:
    def __init__(self, pin_number, freq=50, duty_us=1500, ramp_duration=0.01):
        pin = Pin(pin_number)
        pwm = PWM(pin)
        pwm.freq(freq)
        self.pwm = pwm
        self.duty_us = duty_us
        self.ramp_duration = ramp_duration
        self.current_position = 90  # Start at 90 degrees

    def set_position(self, degrees, custom_ramp_duration=None):
        if custom_ramp_duration is not None:
            ramp_duration = custom_ramp_duration
        else:
            ramp_duration = self.ramp_duration
        if degrees < 0:
            degrees = 0
        elif degrees > 180:
            degrees = 180

        start_position = self.current_position
        end_position = degrees
        steps = int(ramp_duration * 1000)  # Convert seconds to milliseconds
        step_size = (end_position - start_position) / steps

        for _ in range(steps):
            start_position += step_size
            pulse_width = 500 + start_position * 10
            self.pwm.duty_ns(int(pulse_width * 1000))
            time.sleep_ms(1)  # Introduce a small delay
        
        self.current_position = degrees

    def stop(self):
        self.pwm.duty_ns(self.duty_us * 1000)

    def deinit(self):
        self.pwm.deinit()
        
class ContinuousServo:
    def __init__(self, pin_number, freq=50, duty_us=1500):
        pin = Pin(pin_number)
        pwm = PWM(pin)
        pwm.freq(freq)
        self.pwm = pwm
        self.duty_us = duty_us

    def set_speed(self, speed):
        if speed < -100:
            speed = -100
        elif speed > 100:
            speed = 100

        duty_us = self.duty_us + speed * 5
        self.pwm.duty_ns(duty_us * 1000)

    def stop(self):
        self.pwm.duty_ns(self.duty_us * 1000)

    def deinit(self):
        self.pwm.deinit()
