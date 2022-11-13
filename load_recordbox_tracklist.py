import csv

entries = []
with open('/Users/sabjorn/Dropbox/archive/audio/recordings/29-10-22_quadratic_halloween/dataist/29-10-22_quadratic_halloween.txt', newline='') as csvfile:
    for lines in csv.DictReader(csvfile, delimiter=','):
        entries.append(lines)

for l in entries:
    print(l['Track Title'])

