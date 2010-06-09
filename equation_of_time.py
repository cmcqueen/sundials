
import numpy as np
import scipy
import scipy.optimize


SUN_ECCENTRICITY = 0.01671

# The angle from the vernal equinox to the periapsis in the plane of the ecliptic.
SUN_ANGLE_OFFSET = 4.9358

# Angle of tilt of earth's axis--about 23.44 degrees
SUN_OBLIQUITY = 0.40910


def mean_anomaly(day_number_n):
    return day_number_n * (2 * np.pi / 365.242)


@np.vectorize
def eccentric_anomaly(mean_anomaly_value):
    local_sun_eccentricity = SUN_ECCENTRICITY

    def eccentric_anomaly_function(eccentric_anomaly_value):
        return eccentric_anomaly_value - local_sun_eccentricity * np.sin(eccentric_anomaly_value) - mean_anomaly_value

    eccentric_anomaly_value = scipy.optimize.brentq(eccentric_anomaly_function, 0 - 0.0001, 2 * np.pi + 0.0001)
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
    mean_anomaly_value = mean_anomaly(day_number_n)
    eccentric_anomaly_value = eccentric_anomaly(mean_anomaly_value)
    true_anomaly_value = true_anomaly(eccentric_anomaly_value)
    right_ascension_value = right_ascension(true_anomaly_value + SUN_ANGLE_OFFSET)
    eot = mean_anomaly_value + SUN_ANGLE_OFFSET - right_ascension_value
    # Get the angles into the range we want
    eot = (eot + np.pi) % (2 * np.pi) - np.pi
    return eot * (24 * 60 / 2 / np.pi)


def equation_of_time_simple(day_number_n):
    """day_number_n is the day of the year. 1st Jan is day 0.
    Returns the difference between solar time and clock time, in minutes."""
    mean_anomaly_value = mean_anomaly(day_number_n)
    return -7.655 * np.sin(mean_anomaly_value) + 9.873 * np.sin(2 * mean_anomaly_value + 3.588)


#equation_of_time = equation_of_time_simple
equation_of_time = equation_of_time_accurate


def main():
    import matplotlib
    #matplotlib.use('pdf')
    #matplotlib.use('svg')
    from matplotlib import pyplot as plt
    import datetime


    day_numbers = np.arange(0, 365.242, 0.1)
#    plt.plot(day_numbers, equation_of_time(day_numbers))
    date_range = day_numbers + matplotlib.dates.date2num(datetime.date(2000,1,1))
    mean_anomaly_value = mean_anomaly(day_numbers)
    eccentric_anomaly_value = eccentric_anomaly(mean_anomaly_value)
    true_anomaly_value = true_anomaly(eccentric_anomaly_value)
    right_ascension_value = right_ascension(true_anomaly_value + SUN_ANGLE_OFFSET)
#    eot = [ equation_of_time(day_number) for day_number in day_numbers ]
    plt.plot_date(date_range, equation_of_time_simple(day_numbers), '--')
    plt.plot_date(date_range, equation_of_time_accurate(day_numbers), '-')
#    plt.plot_date(date_range, right_ascension_value, '-')

#    plt.xlabel('day number')
#    plt.xlim([min(day_numbers), max(day_numbers)])
    rule = matplotlib.dates.rrulewrapper(matplotlib.dates.MONTHLY)
    loc = matplotlib.dates.RRuleLocator(rule)
    formatter = matplotlib.dates.DateFormatter('%b')
    ax = plt.subplot(111)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=30, fontsize=10)

#    plt.ylabel('solar time - clock time (min)')
    plt.ylabel('clock time - solar time (min)')
    plt.grid(True)

    plt.show()
#    plt.savefig('equation_of_time.pdf')
#    plt.savefig('equation_of_time.svg')
#    plt.savefig('equation_of_time.png')


if __name__ == '__main__':
    main()
