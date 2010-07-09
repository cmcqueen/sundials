#!/usr/bin/env python
"""
Calculation of "equation of time".

References:
    http://en.wikipedia.org/wiki/Equation_of_time
    http://www.sundials.co.uk/equation.htm

Calculations have been done according to the Wikipedia reference.

Dependencies:
    - Python 2.x
    - NumPy
    - SciPy (only strictly needed for the more accurate calculation)
    - matplotlib to plot the graph
"""

import datetime
from collections import namedtuple

import numpy as np
import scipy            # only strictly needed for the more accurate calculation in equation_of_time_accurate()
import scipy.optimize

# Named tuple to hold geographic location
Location = namedtuple('Location', 'latitude, longitude')


# If a location is given, a longitude correction is calculated and included in the graph.
# If the sundial itself includes the longitude correction, just use the 0 value here.
LOCATION = Location(0, 0)
#LOCATION = Location(51.3809, -2.3603)   # Bath, England
#LOCATION = Location(35.10, 138.86)      # Numazu, Japan
#LOCATION = Location(-37.81, 144.96)     # Melbourne, Victoria, Australia


DAYS_PER_TROPICAL_YEAR = 365.242
SUN_ECCENTRICITY = 0.01671

# The angle from the vernal equinox to the periapsis in the plane of the ecliptic.
SUN_ANGLE_OFFSET = 4.9358

# Angle of tilt of earth's axis--about 23.44 degrees
SUN_OBLIQUITY = 0.40910


# Date range for drawing a graph.
DATE_START = datetime.date(2009, 1, 1)
DATE_END = datetime.date(2010, 1, 1)
# Periapsis occurs on a slightly different date each year--varying by a couple
# of days. 4th of January is about the average.
DATE_PERIAPSIS = datetime.date(2009, 1, 4)


def longitude_offset(location):
    """Given a location, return the offset due to longitude, in degrees
    Location's longitude is used. Latitude isn't needed.
    """
    longitude = location.longitude
    longitude_per_hour = (360. / 24)
    longitude_offset = longitude % longitude_per_hour
    if longitude_offset > longitude_per_hour / 2:
        longitude_offset -= longitude_per_hour
    return longitude_offset


def longitude_offset_min(location):
    minute_per_longitude = 24 * 60 / 360.
    return longitude_offset(location) * minute_per_longitude


def mean_anomaly(day_number_n):
    """day_number_n is the number of days from periapsis."""
    return day_number_n * (2 * np.pi / DAYS_PER_TROPICAL_YEAR)


@np.vectorize
def eccentric_anomaly(mean_anomaly_value):
    local_sun_eccentricity = SUN_ECCENTRICITY

    def eccentric_anomaly_function(eccentric_anomaly_value):
        return eccentric_anomaly_value - local_sun_eccentricity * np.sin(eccentric_anomaly_value) - mean_anomaly_value

#    eccentric_anomaly_value = scipy.optimize.brentq(eccentric_anomaly_function, 0 - 0.0001, 2 * np.pi + 0.0001)
    eccentric_anomaly_value = scipy.optimize.fsolve(eccentric_anomaly_function, mean_anomaly_value)
    return eccentric_anomaly_value


def true_anomaly(eccentric_anomaly_value):
    local_sun_eccentricity = SUN_ECCENTRICITY

    half_eccentric_anomaly = eccentric_anomaly_value / 2
    a_x = np.cos(half_eccentric_anomaly)
    a_y = np.sin(half_eccentric_anomaly)
    a_y *= np.sqrt((1 + local_sun_eccentricity) / (1 - local_sun_eccentricity))
    return 2 * np.arctan2(a_y, a_x)


def right_ascension(sun_angle):
    """sun_angle is the angle from the vernal equinox to the Sun in the plane of the ecliptic.
    It is the true_anomaly value plus the SUN_ANGLE_OFFSET."""
    a_x = np.cos(sun_angle)
    a_y = np.sin(sun_angle)
    return np.arctan2(a_y * np.cos(SUN_OBLIQUITY), a_x)


def equation_of_time_accurate(day_number_n):
    """Calculate the equation of time (in min), given a day number.
    
    day_number_n is the number of days from periapsis.
    Returns the difference between solar time and clock time, in minutes.
    This uses a more accurate calculation.
    """
    mean_anomaly_value = mean_anomaly(day_number_n)
    eccentric_anomaly_value = eccentric_anomaly(mean_anomaly_value)
    true_anomaly_value = true_anomaly(eccentric_anomaly_value)
    right_ascension_value = right_ascension(true_anomaly_value + SUN_ANGLE_OFFSET)
    eot = mean_anomaly_value + SUN_ANGLE_OFFSET - right_ascension_value
    # Get the angles into the range we want--that is, -pi to +pi
    eot = (eot + np.pi) % (2 * np.pi) - np.pi
    return eot * (24 * 60 / 2 / np.pi)


def equation_of_time_simple(day_number_n):
    """Calculate the equation of time (in min), given a day number.
    
    day_number_n is the number of days from periapsis.
    Returns the difference between solar time and clock time, in minutes.
    This uses a simple, approximate calculation.
    """
    mean_anomaly_value = mean_anomaly(day_number_n)
    return -7.655 * np.sin(mean_anomaly_value) + 9.873 * np.sin(2 * mean_anomaly_value + 3.588)


#equation_of_time = equation_of_time_simple
equation_of_time = equation_of_time_accurate


def main():
    import matplotlib
    #matplotlib.use('pdf')
    #matplotlib.use('svg')
    from matplotlib import pyplot as plt


    date_range = np.arange(matplotlib.dates.date2num(DATE_START), matplotlib.dates.date2num(DATE_END), 0.1)
    day_numbers = date_range - matplotlib.dates.date2num(DATE_PERIAPSIS)

    # Calculate the accurate and simple calculations of equation of time.
    solar_offset_accurate_min = equation_of_time_accurate(day_numbers) + longitude_offset_min(LOCATION)
    solar_offset_simple_min = equation_of_time_simple(day_numbers) + longitude_offset_min(LOCATION)

    # Plot the graph, either solar vs clock, or vice-versa.
    if 1:
        # Solar time vs clock time
        plt.plot_date(date_range, solar_offset_accurate_min, '-')
#        plt.plot_date(date_range, solar_offset_simple_min, '--')
        plt.ylabel('solar time - clock time (min)')
    else:
        # Clock time vs solar time
        plt.plot_date(date_range, -solar_offset_accurate_min, '-')
#        plt.plot_date(date_range, -solar_offset_simple_min, '--')
        plt.ylabel('clock time - solar time (min)')

    # Set month lines
    ax = plt.subplot(111)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    # Set month labels centred in the middle (actually on day 15) of each month.
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator(bymonthday=15))
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b'))
    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)

    plt.grid(True)

    plt.show()
#    plt.savefig('equation_of_time.pdf')
#    plt.savefig('equation_of_time.svg')
#    plt.savefig('equation_of_time.png')


if __name__ == '__main__':
    main()
