#!/usr/bin/env python
"""
Calculation of sun declination during the year.

References:
    http://en.wikipedia.org/wiki/Declination

Calculations have been done according to the Wikipedia reference.

Dependencies:
    - Python 2.x
    - NumPy
    - SciPy (only strictly needed for the more accurate calculation)
    - matplotlib to plot the graph
"""

import datetime

import numpy as np
import scipy            # only strictly needed for the more accurate calculation in sun_declination_accurate()
import scipy.optimize


DAYS_PER_TROPICAL_YEAR = 365.242

# Angle of tilt of earth's axis--about 23.44 degrees
SUN_OBLIQUITY = 0.40910


# Date range for drawing a graph.
DATE_START = datetime.date(2009, 1, 1)
DATE_END = datetime.date(2010, 1, 1)
# Periapsis occurs on a slightly different date each year--varying by a couple
# of days. 4th of January is about the average.
DATE_SOLSTICE = datetime.date(2008, 12, 21)


def sun_declination_simple(day_number_n):
    """Calculate the sun's declination (in rad), given a day number.
    
    day_number_n is the number of days from solstice.
    Returns the sun's declination, in radians.
    This uses a simple, approximate calculation.
    """
    return -SUN_OBLIQUITY * np.cos((2 * np.pi / DAYS_PER_TROPICAL_YEAR) * day_number_n)


sun_declination = sun_declination_simple
#sun_declination = sun_declination_accurate


def main():
    import matplotlib
    #matplotlib.use('pdf')
    #matplotlib.use('svg')
    from matplotlib import pyplot as plt


    date_range = np.arange(matplotlib.dates.date2num(DATE_START), matplotlib.dates.date2num(DATE_END), 0.1)
    day_numbers = date_range - matplotlib.dates.date2num(DATE_SOLSTICE)

    # Plot the accurate and/or simple calculations of equation of time.
#    plt.plot_date(date_range, np.rad2deg(sun_declination_accurate(day_numbers)), '-')
    plt.plot_date(date_range, np.rad2deg(sun_declination_simple(day_numbers)), '--')

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


    plt.ylabel('declination (deg)')
    plt.grid(True)

    plt.show()
#    plt.savefig('sun_declination.pdf')
#    plt.savefig('sun_declination.svg')
#    plt.savefig('sun_declination.png')


if __name__ == '__main__':
    main()
