import csv

# Dummy example creating CSV with static analysis summaries.
header = ['Tool', 'Issues Found']
data = [
    ['Checkstyle', 5],
    ['PMD', 3],
    ['SpotBugs', 2]
]

with open('sasttools_summary.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(data)
print("Static analysis summary CSV created.")
