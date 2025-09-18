try:
    with open('data.txt', 'r', encoding='utf-8') as in_file:
        loaded_txt = in_file.read().strip().split('\n')
except IOError as error:
    print(f"{error}\nError opening {file}. Terminating program.",
          file=sys.stderr)
    sys.exit(1)

dates = []
systolic = []
diastolic = []
systolic_avgs = []
diastolic_avgs = []

for line in loaded_txt:
    date, sys, dia = line.split()
    dates.append(date)
    systolic.append(int(sys))
    diastolic.append(int(dia))

RUNNING_RANGE = 5

for i in range(0, RUNNING_RANGE-1):
    systolic_avgs.append(-1)
    diastolic_avgs.append(-1)

for i in range(RUNNING_RANGE, len(systolic)+1):
    sum_sys = sum(systolic[i-RUNNING_RANGE:i])
    systolic_avgs.append(sum_sys/RUNNING_RANGE)

    sum_dia = sum(diastolic[i-RUNNING_RANGE:i])
    diastolic_avgs.append(sum_dia/RUNNING_RANGE)

print(f"{RUNNING_RANGE} day running averages")
print("date ~ systolic/diastolic ~ averages")
print("-----------------------------")
for i in range(0, len(systolic)):
    if systolic_avgs[i] == -1:
        averages = ""
    else:
        averages = f"{systolic_avgs[i]} / {diastolic_avgs[i]}"
    
    print(f"{dates[i]} ~ {systolic[i]} / {diastolic[i]} ~ {averages}")

