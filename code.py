from adafruit_circuitplayground import cp
import time
import math

PHYSICS_TICK_RATE = 60 # Physics updates per second
GRAVITY = 1 # Earth gravity multiplier
TRACK_DIAMETER = 0.035 # In meters
FRICTION = 0.01 # 0 is no friction and 1 is immobilized
PIXEL_LOCATIONS = {
    # provides the physcial location for each pixel in degrees from the USB port
    0: 30,
    1: 60,
    2: 90,
    3: 120,
    4: 150,
    5: 210,
    6: 240,
    7: 270,
    8: 300,
    9: 330
}


def resultant_vector_direction (x, y):
    """
    Params:
        x (float): magnitude of x
        y (float): magnitude of y

    Returns:
        direction from 0 (inclusive) to 360 (exclusive)
    """
        # prevents division by zero error when x component is 0
    if x == 0:
        if y > 0:
            # if x is 0 and y is positive, deg is 90
            deg = 90
        else:
            # if x is 0 and y is negative, deg is 270
            deg = 270
    else:
        # deg will be between -90 and 90 (exclusive)
        # (x, y)
        # deg = arctan(y/x)
        # (1, 1)   =>  45
        # (-1, 1)  => -45
        # (-1, -1) =>  45
        # (1, -1)  => -45
        deg = math.degrees(math.atan(y/x))
        # 180 must be added if x is less than 0 to get angle relative to +x direction
        if x < 0:
            # (-1, 1) => -45 + 180 = 135
            # (-1, -1) => 45 + 180 = 225
            deg += 180
        # 360 must be added if x is not less than 0, by y is to get angle relative to +x direction
        elif y < 0:
            # (1, -1) => -45 + 360 = 315
            deg += 360
    return deg


def resultant_vector_magnitude(a, b):
    """
    Returns the resultant magnitude of two component vectors that are orthagonal to each other.

    Params:
        a (float): magnitude of first component vector
        b (float): magnitude of second component vector

    Returns:
        c (float): length of leg C (Hypotenuse)
    """
    if a == 0 and b == 0:
        # Two vectors of length 0 add to 0
        c = 0
    elif a == 0 and b != 0:
        # If a has length of 0, then result is the same as b
        c = abs(b)
    elif a != 0 and b == 0:
        # If b has length of 0, then result is the same as a
        c = abs(a)
    else:
        # Pythagorean theorum finds the result for two orthagonal vectors
        c = math.sqrt((a*a + b*b))
    return c


def acceleration(position, g_direction, g_magnitude):
    """
    Used to simulate the acceleration on a virtual marble that is confined in a circular track.

    This function determines what the acceleration is based on where the marble is,
    the direction of gravity, and the magnitude of gravity.

    Params:
    position (float): 0 - 359.999... position of marble on circular track
    g_direction (float): 0 - 359.999... direction of gravity
    g_magnitude (float): a number >= 0

    Output:
    acceleration (float): >0 means marble will accelerate anti-clockwise around the track
                          NOTE: This does not mean the marble will move anti-clockwise - for example,
                                if the marble is moving clockwise at a considerable speed,
                                an anti-clockwise acceleration will slow it down,
                                but it will still move clockwise
                          <0 means marble will accelerate clockwise around the track
                          The magnitude of acceleration is how great the acceleration is, and it is
                          in the same units as g_magnitude.
    """
    # Finds angle between marble position and gravity
    # This angle can be negative.
    # Negative numbers do not always mean negative acceleration.
    # This is because -90deg is the same as 270deg.
    relative_gravity_angle = g_direction - position

    # Sine of an angle is between -1 and 1. >0 is positive acceleration. <0 is negative acceleration.
    # The number itself is effectively a multiplier that modifies g_magnitude.
    sine_of_rel_angle = math.sin(math.radians(relative_gravity_angle)) #math.sin() works in radians

    # At a relative angles of 90 and -270deg, magnitude is unchanged. This is because
    # At a relative angles of 0, 180, and -180deg, magnitude is 0.
    # At all other relative angles with muliples of 45deg, magnitude is 0.707 that of g_magnitude.
    # NOTE: any angle plus or minus 360 is effectively the same angle as far as sin(angle) goes.
    # Therefore:
    # Relative angles between -360 and -180, and between 0 and 180deg will result in positive acceleration.
    # Relative angles between -180 and 0, and between 180 and 360deg will result in negative acceleration.
    acceleration = sine_of_rel_angle * g_magnitude
    return acceleration


def draw_pixels(position, pixel_locations):
    """
    Takes in the position of the virtual marble, and colors pixels accoridngly
    """
    for pixel in range(0, 10):
        # Angle between position and pixel
        relative_angle = abs(position - pixel_locations[pixel])
        # The furthest away the marble can be from the pixel is 180 degree.s
        # If the relative angle is greater than 180 degrees, it's
        if relative_angle > 180:
            distance = 360 - relative_angle
        else:
            distance = relative_angle
        if distance < 10:
            # Pixel very bright when very close, but rapidly dims with distance
            brightness_multiplier = 0.15 + 0.85 * (1 - distance/10)
        elif distance < 90:
            # Pixel tapers off to 0 when further away
            brightness_multiplier = 0.05 * ((90 - distance)/90)
        else:
            brightness_multiplier = 0
        cp.pixels[pixel] = (255*brightness_multiplier, 0*brightness_multiplier, 0)


if __name__ == '__main__':
    cp.pixels.brightness = 1
    meters_per_degree = (math.pi * TRACK_DIAMETER) / 360 # m/deg
    position = 0 # deg - Intial position of marble
    speed = 0 # m/s - Initial speed of marble
    delta_t = 1 / PHYSICS_TICK_RATE # s - Duration of each tick / time passed
    debug_clock = 0

    while True:
        # Slows down the virtual marble so that it moves realistically
        speed *= (1 - FRICTION)
        # sets up x and y axis such that positive x is in the direction of the USB port
        x = -cp.acceleration[1] # m/s/s
        y = cp.acceleration[0] # m/s/s
        g_direction = resultant_vector_direction(x, y) # deg
        g_magnitude = resultant_vector_magnitude(x, y) # m/s/s
        marble_acceleration = acceleration(position, g_direction, g_magnitude) # m/s/s
        delta_v = marble_acceleration * delta_t # m/s - velocity = acceleration * time
        speed += delta_v # m/s - old speed plus change in speed is new speed
        # speed but represented in degrees around circular track
        # (changes with changes in diameter)
        deg_speed = speed / meters_per_degree # deg/s
        position += deg_speed * delta_t # distance = speed * time
        # Keeps position between 0 and 360
        while position >= 360:
            position -= 360
        while position < 0:
            position += 360

        debug_clock += 1
        # Every second of physics, print the debugging statements
        if debug_clock % 60 == 0:
            # debugging prints:
            print()
            print("delta_t: " + str(delta_t) + "sec/tick")
            print("(x, y): " + str((x, y)) + " m/s/s")
            print("g_direction: " + str(g_direction) + " deg")
            print("g_magnitude: " + str(g_magnitude) + " m/s/s")
            print("Acceleration: " + str(marble_acceleration) + " m/s/s")
            print("delta_v: " + str(delta_v) + " m/s")
            print("speed: " + str(speed) + " m/s")
            print("deg_speed: " + str(deg_speed) + " deg/s")
            print("position: " + str(position) + " deg")

        draw_pixels(position, PIXEL_LOCATIONS)
        time.sleep(delta_t)
