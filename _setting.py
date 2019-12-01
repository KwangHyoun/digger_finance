f = open('_setting.txt', 'r')
lines = f.readlines()

setting = {}
for line in lines:
    item = line.split(" = ")
    setting[item[0]] = item[1]