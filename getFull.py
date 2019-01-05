import csv
import requests
import re
import sys

# Constants for the HTTP request
reqURL = "http://eebo.chadwyck.com.proxy.bc.edu/search/fulltext?ACTION=ByID"
cookieObj = {
    "UID": "bostonc",
    "ezproxy": "CFNh81NhmKRfgfO"
}

startIndex = 1917

with open('crawlResults.csv', newline='', encoding='utf-16') as csvfile:
    counter = 0
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        if counter >= startIndex:
            fulltextURL = reqURL + f"&ID={row[2]}&SOURCE={row[3]}&WARN=N&FILE={row[5]}"

            s = requests.Session()
            response = requests.get(fulltextURL, cookies=cookieObj)
            responsePars = response.text.split('<P>')

            del responsePars[:3]

            if len(responsePars) == 0:
                responsePars = re.sub('[\s\S]*<P ALIGN="CENTER"><A NAME="page-1">', '', response.text, 1).split('<BR>')
                del responsePars[0]
                del responsePars[len(responsePars) - 1]

                with open(f'books/{counter}.txt','a', encoding='utf-16') as fd:
                    for pars in responsePars:
                        filtered = re.sub('<P ALIGN="CENTER">.+</P>', '', pars)
                        filtered = re.sub('<.+>', '', filtered)
                        filtered = re.sub('\n', '', filtered)
                        filtered = re.sub('\s+', ' ', filtered)

                        if filtered != ' ' and filtered != '':
                            fd.write(filtered + '\n')

                    fd.close()
            else:
                print(f"Starting processing book {counter} with {len(responsePars)} lines")
                with open(f'books/{counter}.txt','a', encoding='utf-16') as fd:
                    for pars in responsePars:
                        filtered = re.sub('<P ALIGN="CENTER">.+</P>', '', pars)
                        filtered = re.sub('<.+>', '', filtered)
                        filtered = re.sub('end_check_tcp_subs[^<]+', '', filtered)
                        filtered = re.sub('\n', '', filtered)
                        filtered = re.sub('\s+', ' ', filtered)
                        fd.write(filtered + '\n')

                    fd.close()

            print(f"Finished processing book {counter}")
        counter += 1

        sys.stdout.flush()

# http://eebo.chadwyck.com.ezproxy.cul.columbia.edu/search/fulltext?ACTION=ByID&ID=D00000998449480000&SOURCE=var_spell.cfg&WARN=N&FILE=../session/1546548707_14257
