import csv
import requests
import re
import code

# Constants for the HTTP request
reqURL = "http://eebo.chadwyck.com.ezproxy.cul.columbia.edu/search/fulltext?ACTION=ByID"
cookieObj = {
    "UID": "NYcolumbia",
    "ezproxy": "cUHL7xcVgPWBMGQ"
}

with open('crawlResults.csv', newline='', encoding='utf-16') as csvfile:
    counter = 0
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        fulltextURL = reqURL + f"&ID={row[2]}&SOURCE={row[3]}&WARN=N&FILE={row[5]}"

        s = requests.Session()
        response = requests.get(fulltextURL, cookies=cookieObj)
        responsePars = response.text.split('<P>')

        del responsePars[:3]


        for pars in responsePars:
            with open(f'books/{counter}.txt','a', encoding='utf-16') as fd:
                filtered = re.sub('<P ALIGN="CENTER">.+</P>', '', pars)
                filtered = re.sub('<.+>', '', filtered)
                filtered = re.sub('end_check_tcp_subs[^<]+', '', filtered)
                filtered = re.sub('\n', '', filtered)
                filtered = re.sub('\s+', ' ', filtered)
                fd.write(filtered + '\n')

        counter += 1
        break

# http://eebo.chadwyck.com.ezproxy.cul.columbia.edu/search/fulltext?ACTION=ByID&ID=D00000998449480000&SOURCE=var_spell.cfg&WARN=N&FILE=../session/1546548707_14257
