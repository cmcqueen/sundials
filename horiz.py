
import logging
from collections import namedtuple

import matplotlib
#matplotlib.use('pdf')
#matplotlib.use('svg')
from matplotlib import pyplot as plt
from matplotlib import lines
from matplotlib import text
import numpy as np


#logging.basicConfig(level=logging.DEBUG)

# Named tuple to hold geographic location
Location = namedtuple('Location', 'latitude, longitude')


LOCATION = Location(35.10, 138.86)      # Numazu, Japan
#LOCATION = Location(-37.81, 144.96)     # Melbourne, Victoria, Australia
TIMEZONE = 9
HOUR_LINE_MIN = 5
HOUR_LINE_MAX = 19
GNOMON_LENGTH = 0.9
NUMERAL_OFFSET = 1.07
EXTENT_MAJOR = 1.15
EXTENT_MINOR = 0.65


def equatorial_hour_angle(hour, location, timezone):
    """Midnight is angle 0.
    6 am is angle pi/2.
    midday is angle pi.
    etc."""
    equatorial_angle = (hour - timezone) * 2 * np.pi / 24 + (np.deg2rad(location.longitude))
    logging.debug("For hour %d, equatorial angle %g" % (hour, np.rad2deg(equatorial_angle)))
    return equatorial_angle


def horiz_hour_angle(hour, location, timezone):
    equatorial_angle = equatorial_hour_angle(hour, location, timezone)
    equatorial_angle_from_solar_noon = equatorial_angle - np.pi
    logging.debug("For hour %d, equatorial angle from solar noon %g" % (hour, equatorial_angle_from_solar_noon * 180 / np.pi))
    # negative (am) is towards the west; positive (pm) towards the east
    a_x = np.sin(equatorial_angle_from_solar_noon)
    a_y = np.cos(equatorial_angle_from_solar_noon)
    horiz_angle_from_solar_noon = np.arctan2(np.sin(np.deg2rad(location.latitude)) * a_x, a_y)
    logging.debug("For hour %d, horiz angle from solar noon %g" % (hour, np.rad2deg(horiz_angle_from_solar_noon)))

    if location.latitude >= 0:
        # sun is in the south; shadows fall towards the north
        return np.pi/2 - horiz_angle_from_solar_noon
    else:
        # sun is in the north; shadows fall towards the south
        return -np.pi/2 + horiz_angle_from_solar_noon


def main():
    fig = plt.figure()
    ax1 = fig.add_subplot(111, aspect='equal')
    
    for hour in range(HOUR_LINE_MIN, HOUR_LINE_MAX + 1):
        horiz_angle = horiz_hour_angle(hour, LOCATION, TIMEZONE)
        logging.info("For hour %d, horiz angle %g" % (hour, np.rad2deg(horiz_angle)))
        line = lines.Line2D([0, np.cos(horiz_angle)], [0, np.sin(horiz_angle)])
        ax1.add_line(line)
        hour_text = "%d" % ((hour - 1) % 12 + 1)
        ax1.add_artist(text.Text(np.cos(horiz_angle) * NUMERAL_OFFSET, np.sin(horiz_angle) * NUMERAL_OFFSET, hour_text, ha='center', va='center'))
    
    # Draw the position for the gnomon
    if LOCATION.latitude >= 0:
        gnomon_extent_y = GNOMON_LENGTH
    else:
        gnomon_extent_y = -GNOMON_LENGTH
    gnomon_line = lines.Line2D([0, 0], [0, gnomon_extent_y], color='red')
    ax1.add_line(gnomon_line)
    
    #plt.axis('tight')
    plt.axis('off')
    
    plt.xlim(-EXTENT_MAJOR, EXTENT_MAJOR)
    if LOCATION.latitude >= 0:
        plt.ylim(-EXTENT_MINOR, EXTENT_MAJOR)
    else:
        plt.ylim(-EXTENT_MAJOR, EXTENT_MINOR)
    
    plt.show()
#    plt.savefig('horiz.pdf')
#    plt.savefig('horiz.svg')


main()
