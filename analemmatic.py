"""
Calculation and generation of analemmatic sundial.

References:
    http://pass.maths.org.uk/issue11/features/sundials/index.html
    http://en.wikipedia.org/wiki/Analemmatic_sundial

Calculations have been done according to the Plus Magazine reference.

Dependencies:
    - Python 2.x
    - NumPy
    - matplotlib
"""

import datetime
import logging
from collections import namedtuple

import matplotlib
#matplotlib.use('pdf')
#matplotlib.use('svg')
from matplotlib import pyplot as plt
from matplotlib import lines
from matplotlib import text
import matplotlib.patches
import numpy as np

import sun_declination


#logging.basicConfig(level=logging.DEBUG)

# Named tuple to hold geographic location
Location = namedtuple('Location', 'latitude, longitude')


#LOCATION = Location(51.3809, -2.3603)   # Bath, England
LOCATION = Location(35.10, 138.86)      # Numazu, Japan
#LOCATION = Location(-37.81, 144.96)     # Melbourne, Victoria, Australia
TIMEZONE = 9
HOUR_LINE_MIN = 5
HOUR_LINE_MAX = 19
EXTENT_MAJOR = 1.2
EXTENT_MINOR = 0.9
NUMERAL_OFFSET = 1.1
DATE_SCALE_X_EXTENT = 0.15
DATE_SCALE_TICK_X = 0.1
DATE_SCALE_TEXT_X = 0.025

def equatorial_hour_angle(hour, location, timezone):
    """Midnight is angle 0.
    6 am is angle pi/2.
    midday is angle pi.
    etc."""
    equatorial_angle = (hour - timezone) * 2 * np.pi / 24 + (np.deg2rad(location.longitude))
    logging.debug("For hour %d, equatorial angle %g" % (hour, np.rad2deg(equatorial_angle)))
    return equatorial_angle


def rotated_equatorial_hour_angle(hour, location, timezone):
    """Angles rotated so midday is up on mathematical angle range.
    Midday is pi/2.
    6 am is pi.
    6 pm is 0.
    etc."""
    equatorial_angle = equatorial_hour_angle(hour, location, timezone)
    equatorial_angle_from_solar_noon = equatorial_angle - np.pi
    # Angle currently is angle referenced from solar noon, positive (pm) towards the east.
    # Change to mathematical angle, anticlockwise from 0 in the east.
    return np.pi / 2 - equatorial_angle_from_solar_noon


def analemmatic_horiz_hour_angle(hour, location, timezone):
    equatorial_angle = equatorial_hour_angle(hour, location, timezone)
    equatorial_angle_from_solar_noon = equatorial_angle - np.pi
    logging.debug("For hour %d, equatorial angle from solar noon %g" % (hour, equatorial_angle_from_solar_noon * 180 / np.pi))
    # negative (am) is towards the west; positive (pm) towards the east
    a_x = np.cos(equatorial_angle_from_solar_noon)
    a_y = np.sin(equatorial_angle_from_solar_noon)
    horiz_angle_from_solar_noon = np.arctan2(a_y, a_x * np.sin(np.deg2rad(location.latitude)))
    logging.debug("For hour %d, horiz angle from solar noon %g" % (hour, np.rad2deg(horiz_angle_from_solar_noon)))

    # Angle currently is angle referenced from solar noon, positive (pm) towards the east.
    # Change to mathematical angle, anticlockwise from 0 in the east.
    return np.pi / 2 - horiz_angle_from_solar_noon


def analemmatic_horiz_hour_position(hour, location, timezone):
    rotated_equatorial_angle = rotated_equatorial_hour_angle(hour, location, timezone)
    a_x = np.cos(rotated_equatorial_angle)
    a_y = np.sin(rotated_equatorial_angle)
    a_y *= np.sin(np.deg2rad(location.latitude))
    return (a_x, a_y)


def main():
    fig = plt.figure()
    ax1 = fig.add_subplot(111, aspect='equal')

    # Draw an ellipse arc
    ellipse_angle_min = rotated_equatorial_hour_angle(HOUR_LINE_MIN, LOCATION, TIMEZONE)
    ellipse_angle_max = rotated_equatorial_hour_angle(HOUR_LINE_MAX, LOCATION, TIMEZONE)
    ellipse_rotation = 0
    if LOCATION.latitude < 0:
        # For southern hemisphere, rotate the whole thing around by 180
        # degrees, so "up" is consistently from the sundial viewer's
        # perspective with the sun behind their shoulder.
        ellipse_rotation = 180
    ellipse = matplotlib.patches.Arc(xy=(0,0),  # centre of ellipse
                                     width=2,
                                     height=2*np.sin(np.deg2rad(LOCATION.latitude)),
                                     angle=ellipse_rotation,
                                     theta1=np.rad2deg(ellipse_angle_max),
                                     theta2=np.rad2deg(ellipse_angle_min),
#                                     theta1=0,
#                                     theta2=135
                                     )
    ax1.add_patch(ellipse)

    analemmatic_positions_x = []
    analemmatic_positions_y = []
    for hour in range(HOUR_LINE_MIN, HOUR_LINE_MAX + 1):
        analemmatic_angle = analemmatic_horiz_hour_angle(hour, LOCATION, TIMEZONE)
        (analemmatic_position_x, analemmatic_position_y) = analemmatic_horiz_hour_position(hour, LOCATION, TIMEZONE)
        if LOCATION.latitude < 0:
            # For southern hemisphere, rotate the whole thing around by 180
            # degrees, so "up" is consistently from the sundial viewer's
            # perspective with the sun behind their shoulder.
            analemmatic_angle += np.deg2rad(180)
            (analemmatic_position_x, analemmatic_position_y) = (-analemmatic_position_x, -analemmatic_position_y)
        logging.info("For hour %d, horiz angle %g" % (hour, np.rad2deg(analemmatic_angle)))
        line = lines.Line2D([0, np.cos(analemmatic_angle)], [0, np.sin(analemmatic_angle)])
#        ax1.add_line(line)
#        ax1.plot(analemmatic_position_x, analemmatic_position_y, '.')
        analemmatic_positions_x.append(analemmatic_position_x)
        analemmatic_positions_y.append(analemmatic_position_y)
        hour_text = "%d" % ((hour - 1) % 12 + 1)
#        ax1.add_artist(text.Text(np.cos(analemmatic_angle) * NUMERAL_OFFSET, np.sin(analemmatic_angle) * NUMERAL_OFFSET, hour_text, ha='center', va='center'))
        ax1.add_artist(text.Text(analemmatic_position_x * NUMERAL_OFFSET, analemmatic_position_y * NUMERAL_OFFSET, hour_text, ha='center', va='center'))

    ax1.plot(analemmatic_positions_x, analemmatic_positions_y, '.')

    # Draw date scale
    # Max line
    dates_y = []
    for sun_angle in [-sun_declination.SUN_OBLIQUITY, sun_declination.SUN_OBLIQUITY]:
        date_y = np.tan(sun_angle) * np.cos(np.deg2rad(LOCATION.latitude))
        dates_y.append(date_y)
        line = lines.Line2D([-DATE_SCALE_X_EXTENT, DATE_SCALE_X_EXTENT], [date_y, date_y])
        ax1.add_line(line)
    line = lines.Line2D([0,0], dates_y)
    ax1.add_line(line)

    DATE_SOLSTICE = datetime.date(2008, 12, 21)
    month_starts_y = []
    month_start_slopes = []
    for month_number in range(1, 12 + 1):
        month_start = datetime.date(2009, month_number, 1)
        day_number = matplotlib.dates.date2num(month_start) - matplotlib.dates.date2num(DATE_SOLSTICE)
        sun_angle = sun_declination.sun_declination(day_number)
        sun_angle2 = sun_declination.sun_declination(day_number + 0.001)
        month_start_slope = 1 if sun_angle2 >= sun_angle else -1
        month_start_slopes.append(month_start_slope)
        if LOCATION.latitude < 0:
            sun_angle = -sun_angle
            sun_angle2 = -sun_angle2
#        month_start_slope = 1 if sun_angle2 >= sun_angle else -1
#        month_start_slopes.append(month_start_slope)
        month_start_y = np.tan(sun_angle) * np.cos(np.deg2rad(LOCATION.latitude))
        month_starts_y.append(month_start_y)
    month_starts_y.append(month_starts_y[0])
    month_start_slopes.append(month_start_slopes[0])
    for month_number in range(1, 12 + 1):
        month_start_y = month_starts_y[month_number - 1]
        month_end_y = month_starts_y[month_number]
        month_start_slope = month_start_slopes[month_number - 1]
        month_end_slope = month_start_slopes[month_number]

        # Add tick mark for month start
        line = lines.Line2D([0, month_start_slope * DATE_SCALE_TICK_X], [month_start_y, month_start_y])
        ax1.add_line(line)

        # Add text for month name, in the middle of the month
        if month_start_slope == month_end_slope:
            text_y = (month_start_y + month_end_y) / 2
            month_name = datetime.date(2009,month_number,1).strftime("%b")
            ha = 'left' if month_start_slope >= 0 else 'right'
            ax1.add_artist(text.Text(DATE_SCALE_TEXT_X * month_start_slope, text_y, month_name, ha=ha, va='center'))


    # Draw a compass arrow
    if 0:
        if LOCATION.latitude >= 0:
            # Up for northern hemisphere
            ax1.add_artist(text.Text(0, -0.25, "N", ha='center', va='center'))
            arrow = matplotlib.patches.Arrow(0, -0.6, 0, 0.3, width=0.1, edgecolor='none')
            ax1.add_patch(arrow)
        else:
            # Down for the southern hemisphere
            ax1.add_artist(text.Text(0, -0.6, "N", ha='center', va='center'))
            arrow = matplotlib.patches.Arrow(0, -0.25, 0, -0.3, width=0.1, edgecolor='none')
            ax1.add_patch(arrow)

    #plt.axis('tight')
    plt.axis('off')
    
    plt.xlim(-EXTENT_MAJOR, EXTENT_MAJOR)
    plt.ylim(-EXTENT_MINOR, EXTENT_MAJOR)

    plt.show()
#    plt.savefig('analemmatic.pdf')
#    plt.savefig('analemmatic.svg')
#    plt.savefig('analemmatic.png')


main()
