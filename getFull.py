import csv

with open('results.csv', newline='', encoding='utf-16') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        print(row)
