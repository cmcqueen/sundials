#!/usr/bin/env python3
"""
Calculation and generation of analemmatic sundial.

References:
    Plus Magazine http://pass.maths.org.uk/issue11/features/sundials/index.html
    Wikipedia     http://en.wikipedia.org/wiki/Analemmatic_sundial

Calculations have been done according to the Plus Magazine reference.

Dependencies:
    - Python 2.x
    - NumPy
    - matplotlib
"""

import datetime
import logging
from collections import namedtuple
import sys

import matplotlib
#matplotlib.use('pdf')
#matplotlib.use('svg')
from matplotlib import pyplot as plt
from matplotlib import lines
from matplotlib import text
import matplotlib.patches
import numpy as np

import sun_declination


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Named tuple to hold geographic location
Location = namedtuple('Location', 'latitude, longitude, timezone, location')


if True:
    LOCATION = Location(-37.81, 144.96, 10, 'Melbourne, Victoria, Australia')
    HOUR_LINE_MIN = 5
    HOUR_LINE_MAX = 20
    EXTENT_MAJOR = 1.2
    EXTENT_MINOR = 0.75
elif True:
    LOCATION = Location(35.10, 138.86, 9, 'Numazu, Japan')
    HOUR_LINE_MIN = 4
    HOUR_LINE_MAX = 19
    EXTENT_MAJOR = 1.2
    EXTENT_MINOR = 0.75
else:
    LOCATION = Location(51.3809, -2.3603, 0, 'Bath, England')
    HOUR_LINE_MIN = 3
    HOUR_LINE_MAX = 21
    EXTENT_MAJOR = 1.2
    EXTENT_MINOR = 1.1
NUMERAL_OFFSET = 1.1
DATE_SCALE_X_EXTENT = 0.15
DATE_SCALE_TICK_X = 0.1
DATE_SCALE_TEXT_X = 0.025

def equatorial_hour_angle(hour, location):
    """Midnight is angle 0.
    6 am is angle pi/2.
    midday is angle pi.
    etc."""
    equatorial_angle = (hour - location.timezone) * 2 * np.pi / 24 + (np.deg2rad(location.longitude))
    logging.getLogger("hour.angle.equ").debug("For hour %d, equatorial angle %g" % (hour, np.rad2deg(equatorial_angle)))
    return equatorial_angle


def rotated_equatorial_hour_angle(hour, location):
    """Angles rotated so midday is up on mathematical angle range.
    Midday is pi/2.
    6 am is pi.
    6 pm is 0.
    etc."""
    equatorial_angle = equatorial_hour_angle(hour, location)
    equatorial_angle_from_solar_noon = equatorial_angle - np.pi
    # Angle currently is angle referenced from solar noon, positive (pm) towards the east.
    # Change to mathematical angle, anticlockwise from 0 in the east.
    return np.pi / 2 - equatorial_angle_from_solar_noon


def analemmatic_horiz_hour_angle(hour, location):
    equatorial_angle = equatorial_hour_angle(hour, location)
    equatorial_angle_from_solar_noon = equatorial_angle - np.pi
    logging.getLogger("hour.angle.equ.noon").debug("For hour %d, equatorial angle from solar noon %g" % (hour, equatorial_angle_from_solar_noon * 180 / np.pi))
    # negative (am) is towards the west; positive (pm) towards the east
    a_x = np.cos(equatorial_angle_from_solar_noon)
    a_y = np.sin(equatorial_angle_from_solar_noon)
    horiz_angle_from_solar_noon = np.arctan2(a_y, a_x * np.sin(np.deg2rad(location.latitude)))
    logging.getLogger("hour.angle.horiz.noon").debug("For hour %d, horiz angle from solar noon %g" % (hour, np.rad2deg(horiz_angle_from_solar_noon)))

    # Angle currently is angle referenced from solar noon, positive (pm) towards the east.
    # Change to mathematical angle, anticlockwise from 0 in the east.
    return np.pi / 2 - horiz_angle_from_solar_noon


def analemmatic_horiz_hour_position(hour, location):
    rotated_equatorial_angle = rotated_equatorial_hour_angle(hour, location)
    a_x = np.cos(rotated_equatorial_angle)
    a_y = np.sin(rotated_equatorial_angle)
    a_y *= np.sin(np.deg2rad(location.latitude))
    logging.getLogger("hour.pos").debug("For hour %d, x-y position (%g, %g)" % (hour, a_x, a_y))
    return (a_x, a_y)


def main():
    fig = plt.figure(num=LOCATION.location)
#    ax1 = fig.add_subplot(111, aspect='equal')
    ax1 = fig.add_axes([0,0,1.0,1.0], aspect='equal')

    # Calculate ellipse parameters
    ellipse_major_axis = 1.0
    ellipse_minor_axis = ellipse_major_axis * np.sin(np.deg2rad(LOCATION.latitude))
    ellipse_foci_offset = np.sqrt(ellipse_major_axis**2 - ellipse_minor_axis**2)
    ellipse_logger = logging.getLogger("ellipse")
    ellipse_logger.info("Ellipse semimajor axis length %g" % ellipse_major_axis)
    ellipse_logger.info("Ellipse semiminor axis length %g" % ellipse_minor_axis)
    ellipse_logger.info("Ellipse foci x offset %g" % ellipse_foci_offset)
    # Draw an ellipse arc
    ellipse_pos_min = analemmatic_horiz_hour_position(HOUR_LINE_MIN, LOCATION)
    ellipse_angle_min = np.arctan2(ellipse_pos_min[1], ellipse_pos_min[0])
    ellipse_pos_max = analemmatic_horiz_hour_position(HOUR_LINE_MAX, LOCATION)
    ellipse_angle_max = np.arctan2(ellipse_pos_max[1], ellipse_pos_max[0])
    ellipse_rotation = 0
    if LOCATION.latitude < 0:
        # For southern hemisphere, rotate the whole thing around by 180
        # degrees, so "up" is consistently from the sundial viewer's
        # perspective with the sun behind their shoulder.
        ellipse_rotation = 180
    ellipse = matplotlib.patches.Arc(xy=(0,0),  # centre of ellipse
                                     width=2 * ellipse_major_axis,
                                     height=2 * ellipse_minor_axis,
                                     angle=ellipse_rotation,
                                     theta1=np.rad2deg(ellipse_angle_max),
                                     theta2=np.rad2deg(ellipse_angle_min),
                                    )
    ax1.add_patch(ellipse)

    analemmatic_positions_x = []
    analemmatic_positions_y = []
    for hour in range(HOUR_LINE_MIN, HOUR_LINE_MAX + 1):
        analemmatic_angle = analemmatic_horiz_hour_angle(hour, LOCATION)
        (analemmatic_position_x, analemmatic_position_y) = analemmatic_horiz_hour_position(hour, LOCATION)
        if LOCATION.latitude < 0:
            # For southern hemisphere, rotate the whole thing around by 180
            # degrees, so "up" is consistently from the sundial viewer's
            # perspective with the sun behind their shoulder.
            analemmatic_angle += np.deg2rad(180)
            (analemmatic_position_x, analemmatic_position_y) = (-analemmatic_position_x, -analemmatic_position_y)
        logging.getLogger("hour.angle.horiz").info("For hour %d, horiz angle %g" % (hour, np.rad2deg(analemmatic_angle)))
        logging.getLogger("hour.pos").info("For hour %d, x-y position (%g, %g)" % (hour, analemmatic_position_x, analemmatic_position_y))
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
    datescale_logger = logging.getLogger("datescale")
    # Max and min lines
    dates_y = []
    for sun_angle in [-sun_declination.SUN_OBLIQUITY, sun_declination.SUN_OBLIQUITY]:
        date_y = np.tan(sun_angle) * np.cos(np.deg2rad(LOCATION.latitude))
        dates_y.append(date_y)
        line = lines.Line2D([-DATE_SCALE_X_EXTENT, DATE_SCALE_X_EXTENT], [date_y, date_y])
        ax1.add_line(line)
    # Draw vertical line of date scale
    line = lines.Line2D([0,0], dates_y)
    ax1.add_line(line)
    datescale_logger.info("Date scale max and min y positions at %g and %g" % tuple(dates_y))

    # Draw month ticks and month labels on date scale
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
        month_name = month_start.strftime("%b")
        datescale_logger.info("For beginning of %s, y position %g" % (month_name, month_start_y))
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
    if LOCATION.latitude >= 0:
        # Up for northern hemisphere
        ax1.add_artist(text.Text(0.5, 0.15, "N", ha='center', va='center'))
        arrow = matplotlib.patches.Arrow(0.5, -0.15, 0, 0.25, width=0.08, edgecolor='none')
        ax1.add_patch(arrow)
    else:
        # Down for the southern hemisphere
        ax1.add_artist(text.Text(0.5, -0.15, "N", ha='center', va='center'))
        arrow = matplotlib.patches.Arrow(0.5, 0.15, 0, -0.25, width=0.08, edgecolor='none')
        ax1.add_patch(arrow)

#    plt.axis('tight')
    plt.axis('off')
    
    plt.xlim(-EXTENT_MAJOR, EXTENT_MAJOR)
    plt.ylim(-EXTENT_MINOR, EXTENT_MINOR)

#    plt.savefig('analemmatic.pdf')
#    plt.savefig('analemmatic.svg')
#    plt.savefig('analemmatic.png')
    plt.show()


if __name__ == '__main__':
    main()
