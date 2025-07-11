"""Model retirement income using Monte Carlo simulation."""
import sys
import random
import matplotlib.pyplot as plt
# pylint: disable=R0914, C0103

def pr_red(output):
    """Print string to console, colored red."""
    print(f"\033[91m{output}\033[00m")

def read_to_list(file_name):
    """Open a file of data in percent, convert to decimal & return a list."""
    with open(file_name, 'r', encoding='utf-8') as in_file:
        lines = [float(line.strip()) for line in in_file]
        decimal = [round(line / 100, 5) for line in lines]
        return decimal

def default_input(prompt, default=None):
    """Allow use of default values in input."""
    prompt = f"{prompt} [{default}]"
    response = input(prompt)
    if not response and default:
        return default
    return response

print("\nNote: Input data should be in percent, not decimal!\n")
try:
    bonds = read_to_list('10-yr_TBond_returns_1926-2013_pct.txt')
    stocks = read_to_list('SP500_returns_1926-2013_pct.txt')
    blend_40_50_10 = read_to_list('S-B-C_blend_1926-2013_pct.txt')
    blend_50_50 = read_to_list('S-B_blend_1926-2013_pct.txt')
    infl_rate = read_to_list('annual_infl_rate_1926-2013_pct.txt')
except IOError as exception:
    print(f"{exception}. \nTerminating program.")
    sys.exit(1)

investment_type_args = {'bonds': bonds, 'stocks': stocks,
                        'sb_blend': blend_50_50, 'sbc_blend': blend_40_50_10}

print("   stocks = SP500")
print("    bonds = 10-yr Treasury Bond")
print(" sb_blend = 50% SP500 / 50% TBond")
print("sbc_blend = 40% SP500 / 50% TBond / 10% Cash")
print("Press ENTER to take default value shown in [brackets].\n")

invest_type = default_input("Enter investmet type: (stocks, bonds, sb_blend,"\
                            " sbc_blend): \n", 'bonds').lower()
while invest_type not in investment_type_args:
    invest_type = input("Invalid investment. Enter investment type "\
                        "as listed in prompt: ")

start_value = default_input("Input starting value of investments: \n", \
                            '2000000')
while not start_value.isdigit():
    start_value = input("Invalid input! Input integer only: ")

withdrawal = default_input("Input annual pre-tax withdrawal" \
                           " (today's $): \n", '80000')
while not withdrawal.isdigit():
    withdrawal = input("Invalid input! Input integer only: ")

min_years = default_input("Input minimum years in retirement: \n", '18')
while not min_years.isdigit():
    min_years = input("Invalid input! Input integer only: ")

most_likely_years = default_input("Input most-likely years in retirement: \n",
                                  '25')
while not most_likely_years.isdigit():
    most_likely_years = input("Invalid input! Input integer only: ")

max_years = default_input("Input maximum years in retirement: \n",
                          '40')
while not max_years.isdigit():
    max_years = input("Invalid input! Input integer only: ")

num_cases = default_input("Input number of cases to rn: \n", '50000')
while not num_cases.isdigit():
    num_cases = input("Invalid input! Input integer only: ")

if (not int(min_years) < int(most_likely_years) < int(max_years)
    or int(max_years) > 99):
    pr_red("\nProblem with input years.")
    pr_red("Requires Min < ML < Max with Max <= 99")
    sys.exit(1)

def montecarlo(returns):
    """Run MCS & return investment value at end-of-plan & bankrupt count."""
    case_count = 0
    bankrupt_count = 0
    outcome = []

    while case_count < int(num_cases):
        investments = int(start_value)
        start_year = random.randrange(0, len(returns))
        duration = int(random.triangular(int(min_years), int(max_years),
                                         int(most_likely_years)))
        end_year = start_year + duration
        lifespan = list(range(start_year, end_year))
        bankrupt = 'no'

        lifespan_returns = []
        lifespan_infl = []
        for i in lifespan:
            lifespan_returns.append(returns[i % len(returns)])
            lifespan_infl.append(infl_rate[i % len(returns)])

        for index, i in enumerate(lifespan_returns):
            infl = lifespan_infl[index]

            if index == 0:
                withdraw_infl_adj = int(withdrawal)
            else:
                withdraw_infl_adj = int(withdraw_infl_adj * (1 + infl))

            investments -= withdraw_infl_adj
            investments = int(investments * (1 + i))

            if investments <= 0:
                bankrupt = 'yes'
                break

        if bankrupt == 'yes':
            outcome.append(0)
            bankrupt_count += 1
        else:
            outcome.append(investments)

        case_count += 1

    return outcome, bankrupt_count

def bankrupt_prob(outcome, bankrupt_count):
    """Calculate and return chance of running out of money & other stats."""
    total = len(outcome)
    odds = round(100 * bankrupt_count / total, 1)

    print(f"\nInvestment type: {invest_type}")
    print(f"Starting value: ${int(start_value):,}")
    print(f"Annual withdrawal: ${int(withdrawal):,}")
    print(f"Years in retirement (min-ml-max): "
          f"{min_years}-{most_likely_years}-{max_years}")
    print(f"Number of runs: {len(outcome):,}")
    print(f"Odds of running out of money: {odds}%")
    print(f"Average outcome: ${int(sum(outcome)/total):,}")
    print(f"Minimum outcome: ${min(i for i in outcome):,}")
    print(f"Maximum outcome: ${max(i for i in outcome):,}")

    return odds

def main():
    """Call MCS & bankrupt functions and draw bar chart of results."""
    outcome, bankrupt_count = montecarlo(investment_type_args[invest_type])
    odds = bankrupt_prob(outcome, bankrupt_count)

    plotdata = outcome[:3000]

    plt.figure(f"Outcome by Case (showing first {len(plotdata)} runs)",
               figsize=(16,5))
    index = [i + 1 for i in range(len(plotdata))]
    plt.bar(index, plotdata, color='black')
    plt.xlabel('Simulated Lives', fontsize=18)
    plt.ylabel('$ Remaining', fontsize=18)
    plt.ticklabel_format(style='plain', axis='y')
    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x,
                                                         loc: f"{int(x):,}"))
    plt.title(f"Probability of running out of money = {odds}%",
              fontsize=20, color='red')
    plt.show()

if __name__ == '__main__':
    main()
