
import numpy as np


def M(day_number_n):
    return day_number_n * (2 * np.pi / 365.242)

def equation_of_time_simple(day_number_n):
    """day_number_n is the day of the year. 1st Jan is day 0.
    Returns the difference between solar time and clock time, in minutes."""
    M_value = M(day_number_n)
    return -7.655 * np.sin(M_value) + 9.873 * np.sin(2 * M_value + 3.588)

equation_of_time = equation_of_time_simple


def main():
    import matplotlib
    #matplotlib.use('pdf')
    #matplotlib.use('svg')
    from matplotlib import pyplot as plt
    import datetime


    day_numbers = np.arange(0, 365.242, 0.01)
#    plt.plot(day_numbers, equation_of_time(day_numbers))
    date_range = day_numbers + matplotlib.dates.date2num(datetime.date(2000,1,1))
    plt.plot_date(date_range, -equation_of_time(day_numbers), '-')

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
