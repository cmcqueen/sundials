
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


    day_numbers = np.arange(0, 365.242, 0.01)
    plt.plot(day_numbers, equation_of_time(day_numbers))

    plt.axis('tight')
    plt.show()
#    plt.savefig('horiz.pdf')
#    plt.savefig('horiz.svg')
#    plt.savefig('horiz.png')


if __name__ == '__main__':
    main()
