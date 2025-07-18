"""Assess a set of data for potential fraud using Benford's Law."""
import sys
import math
from collections import defaultdict
import matplotlib.pyplot as plt

BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

def pr_red(string):
    """Print string to console, colored red."""
    print(f"\033[91m {string}\033[00m")

def load_data(filename):
    """Open a text file & return a list of strings."""
    with open(filename, 'r', encoding='utf-8') as in_file:
        return in_file.read().strip().split('\n')

def count_first_digits(data_list):
    """Count 1st digits in list of numbers; return counts & frequency."""
    first_digits = defaultdict(int)
    for sample in data_list:
        if sample == '':
            continue
        try:
            int(sample)
        except ValueError as err:
            pr_red(err)
            pr_red("Samples must be integers. Exiting.")
            sys.exit(1)
        first_digits[sample[0]] += 1
    data_count = [v for (k, v) in sorted(first_digits.items())]
    total_count = sum(data_count)
    data_pct = [(i / total_count) * 100 for i in data_count]
    return data_count, data_pct, total_count

def get_expected_counts(total_count):
    """Return expected Benford's law counts for a total sample count."""
    return [round(p * total_count/100) for p in BENFORD]

def chi_square_test(data_count, expected_counts):
    """Return boolean on chi-square test (8 deg. freedom & P-val 0.05)."""
    chi_square_stat = 0
    for data, expected in zip(data_count, expected_counts):
        chi_square = math.pow(data - expected, 2)
        chi_square_stat += chi_square / expected

    print(f"\nChi Squared Test Statistic = {chi_square_stat:.3f}")
    print("Critical value at a P-value o 0.05 is 15.51.")

    return chi_square_stat < 15.51

def bar_chart(data_pct):
    """Make bar chart of observed vs expected 1st-digit frequency (%)."""
    _, axes = plt.subplots()

    index = [i + 1 for i in range(len(data_pct))]

    # following usage from the text has since been deprecated - use next line
    #fig.canvas.set_window_title('Percentage First Digits')
    plt.get_current_fig_manager().set_window_title('Percentage First Digits')
    axes.set_title('Data vs. Benford Values', fontsize=15)
    axes.set_ylabel('Frequency (%)', fontsize=16)
    axes.set_xticks(index)
    axes.set_xticklabels(index, fontsize=14)

    rects = axes.bar(index, data_pct, width=0.95, color='black', label='Data')

    for rect in rects:
        height = rect.get_height()
        axes.text(rect.get_x() + rect.get_width()/2, height,
                  f'{height:0.1f}', ha='center', va='bottom',
                  fontsize=13)

    axes.scatter(index, BENFORD, s=150, c='red', zorder=2, label='Benford')

    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.legend(prop={'size':15}, frameon=False)

    plt.show()

def main():
    """Call functions and print stats."""
    while True:
        filename = input("\nName of file with COUNT data: ")
        try:
            data_list = load_data(filename)
        except IOError as err:
            pr_red(f"{err}. Try again.")
        else:
            break

    data_count, data_pct, total_count = count_first_digits(data_list)
    expected_counts = get_expected_counts(total_count)
    print(f"\nobserved counts = {data_count}")
    print(f"expected counts = {expected_counts}\n")

    print("First Digit Probabilities:")
    for i in range(1,10):
        print(f"{i}: observed: {data_pct[i-1]/100:.3f} "
              f"expected: {BENFORD[i-1]/100:.3f}")

    if chi_square_test(data_count, expected_counts):
        print("Observed distribution matches expected distribution.")
    else:
        pr_red("Observed distribution does not match expected distribution.")

    bar_chart(data_pct)

if __name__ == '__main__':
    main()
