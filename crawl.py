import requests
import re

# Constants for the HTTP request
reqURL = "http://eebo.chadwyck.com.proxy.bc.edu/search"
cookieObj = {
    "UID": "bostonc",
    "ezproxy": "powMRwiHuL7Qe1u"
}
formData = "ACTION=SearchOrBrowse&SCREEN=search_basic.htx&BFILE=&BSCFILE=&SEARCHSCREEN=search_basic.htx&SOURCE=var_spell.cfg&DUMMYHIT=%3CEEBOID%3E&CRITERIA=&SPELLING_VARIANTS=Y&ECCO=&ALL_KEYWORD=us&B_ALL_KEYWORD=&CIT_KEYWORD=&FT_KEYWORD=&COMBINE_KEYWORDS=&LIMIT=WITH_FULLTEXT&AUTHOR=&B_AUTHOR=&TITLE=&B_TITLE=&SUBJECT=&B_SUBJECT=&BIBNUM=&DATE1=1473&DATE2=1900&DISPLAY=DATE_ASC&SIZE=99&SEARCH=Search&ALL_KEYWORD_SPELLING_VARIANTS=&CIT_KEYWORD_SPELLING_VARIANTS=&FT_KEYWORD_SPELLING_VARIANTS="
retrieveFrom = 1
retrieveCap = 24855

# HTML tags to designate certain parts
bookTitleTag="'CITATIONS', 'DATE_ASC', 'var_spell.cfg', '', '', 'Y' )</SCRIPT><TD WIDTH=\"40\" VALIGN=\"TOP\"></TD><TD><B>"
dateTag = "<BR><SPAN CLASS=\"boldtext\">Date:</SPAN"
fulltextTag = "<SCRIPT>fturl='';write_fulltext_start_link('"

# Aggregation Vars 
bookTitle = ""
date = ""
bookID = ""
parseFile = ""
order = ""
sessionFile = ""

parsedTitle = False
parsedDate = False
parsedFullText = False

# fd.write('title,date,bookID,parseFile,order,sessionFile')

with open('results.csv','a', encoding='utf-16') as fd:
    while retrieveFrom < retrieveCap:
        print("Retrieving from " + str(retrieveFrom) + " to " + str(retrieveFrom + 99))
        indexedFormData = formData + "&RETRIEVEFROM=" + str(retrieveFrom)
        s = requests.Session()
        response = requests.post(reqURL, data=indexedFormData, cookies=cookieObj)
        responseLines = response.text.split("\n")

        for line in responseLines:
            if bookTitleTag in line:
                m = re.search('<B>\d+\.&nbsp;(.+)</B>', line)
                bookTitle = m.group(1).replace(',', ';')
                parsedTitle = True
                
            if dateTag in line:
                m = re.search('<BR><SPAN CLASS="boldtext">Date:</SPAN>\s(.+)', line)
                date = m.group(1).replace(',', ';')
                parsedDate = True

            if fulltextTag in line:
                m = re.search("<SCRIPT>fturl='';write_fulltext_start_link\('(.+)','(.+)','(.+)','([^']+)", line)
                bookID = m.group(1).replace(',', ';')
                parseFile = m.group(2).replace(',', ';')
                order = m.group(3).replace(',', ';')
                sessionFile = m.group(4).replace(',', ';')
                parsedFullText = True

            if parsedTitle and parsedDate and parsedFullText:
                fd.write(bookTitle + ',' + date + ',' + bookID + ',' + parseFile + ',' + order + ',' + sessionFile + '\n')
                
                parsedTitle = False
                parsedDate = False
                parsedFullText = False

        retrieveFrom += 99
