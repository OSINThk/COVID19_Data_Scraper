import csv

def write_to_csv(country,country_data):
    with open(country+'.csv', mode='w') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in country_data:
            spamwriter.writerow([row.name,row.coordinates.lat,row.coordinates.long,row.cases])
