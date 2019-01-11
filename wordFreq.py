import re
import string
import os
import sys
import code

def parseBook(inputFile):
    bookFile = open(inputFile, 'r', encoding='utf-16') # Establish a file reader
    book = bookFile.read() # Read the file
    bookWithoutPunctuation = book.translate(str.maketrans('','',string.punctuation)) # Get rid of punctuation
    bookWithoutNumbers = bookWithoutPunctuation.translate(str.maketrans('','',string.digits))
    bookList = re.split(' |\r\n|\n', bookWithoutNumbers) # Split by space or newline
    bookListWithoutEmpty = list(filter(None, bookList)) # Remove empty elements
    cleanBook = map(lambda word: word.lower(), bookListWithoutEmpty) # Convert all letters to lowercase
    return list(cleanBook)

def matchDates(title, pub):
    titleDates = re.findall('(\d+)', title) # Match all groups of digits
    if "039" in titleDates: # Deletes weird #039 notation
        titleDates.remove("039")
    titleRange = '-' in title
    titleCent = "cent" in title

    if titleCent: # If "cent" exists in the title
        for i in range(len(titleDates)):
            if len(titleDates[i]) == 2: # Replace all 2 digit numbers with corresponding years
                titleDates[i] = str(int(titleDates[i]) * 100)

    # If number of ints > 2, but 2 of them are years, then find the 2 years and convert into a range
    if len(titleDates) == 3 and len(''.join(titleDates)) > 8:
        lower = titleDates[1]
        upper = titleDates[1]
        if len(titleDates[0]) == 4:
            lower = titleDates[0]
        if len(titleDates[2]) == 4:
            upper = titleDates[2]

        titleDates = [lower, upper]

    pubDates = re.findall('(\d+)', pub) # Match all groups of digits
    pubRange = '-' in pub

    if len(titleDates) == 0:
        # If title has no date then the pub date is automatically correct
        return True
    elif len(titleDates) == 1:
        # If the title has a date less than 4 digits, it is automatically outside of publication range (1400-1850) => bad
        # The date in the title must be larger than pub date (since it refers to author's death)
        return (len(titleDates[0]) == 4) and int(titleDates[0]) >= int(pubDates[0])
    elif len(titleDates) == 2 and titleRange: # Two years detected with a range symbol in title
        if len(pubDates) == 1:
            return (int(titleDates[0]) <= int(pubDates[0])) and (int(titleDates[1]) >= int(pubDates[0]))
        elif len(pubDates) == 2 and pubRange: # Two years detected with a range symbol in pub date
            lower = (int(titleDates[0]) < int(pubDates[0])) and (int(titleDates[1]) < int(pubDates[0]))
            upper = (int(titleDates[0]) > int(pubDates[1])) and (int(titleDates[1]) > int(pubDates[1]))
            return (not lower) and (not upper)
    return False

def parseIndexes():
    indexObj = {}
    indexFile = open('crawlResults.csv', 'r', encoding='utf-16')
    index = indexFile.read().split('\n')
    for i in range(len(index)):
        bookData = index[i].split(',')
        if len(bookData) >= 2:
            if matchDates(bookData[0], bookData[1]):
                indexObj[i] = [bookData[0], bookData[1]]
    return indexObj

def getMasterList():
    wordFile = open('Word-list.txt', 'r', encoding='utf-16')
    return list(map(lambda word: word.strip().lower(), wordFile.read().split(',')))


masterList = getMasterList()
indexObj = parseIndexes()
yearsObj = {}

with open('resultTitle.csv', 'w', encoding='utf-16') as f:
    headerStr = "date, title, total words, total climate,"
    for word in masterList:
        headerStr += word + ','
    headerStr = headerStr[:-1] # Remove last comma
    headerStr += '\n' # Complete the header line
    f.write(headerStr)

    counter = 0
    for filename in os.listdir(os.getcwd() + '/books'):
        sys.stdout.write('\r')
        sys.stdout.write(str(round(counter / 19046, 3)) + '% complete\r')
        sys.stdout.flush()

        fileIndex = int(re.findall('(\d+)', filename)[0])
        if fileIndex in indexObj: # If the date of the file makes sense
            dic = {} # Establish a dictionary
            wordList = parseBook('books/' + filename)
            totalClimate = 0
            for word in wordList:
                if word in masterList:
                    totalClimate += 1
                    if word in dic:
                        dic[word] += 1
                    else:
                        dic[word] = 1

            pubDates = re.findall('(\d+)', indexObj[fileIndex][1])
            pubDate = pubDates[0]
            if len(pubDates) > 1:
                pubDate = str(int((int(pubDates[0]) + int(pubDates[1])) / 2))

            writeStr = pubDate + ',' + indexObj[fileIndex][0] + ',' + str(len(wordList)) + ',' + str(totalClimate) + ','

            for word in masterList:
                if word in dic:
                    writeStr += str(dic[word]) + ','
                else:
                    writeStr += "0,"

            writeStr = writeStr[:-1] # Remove the last comma
            writeStr += '\n'
            f.write(writeStr)

            if pubDate in yearsObj:
                yearObj = yearsObj[pubDate]
                yearObj["totWords"] += len(wordList)
                yearObj["totClimate"] += totalClimate
                for word in masterList:
                    if word in dic:
                        yearObj[word] += dic[word]
            else:
                yearsObj[pubDate] = {
                    "totWords": len(wordList),
                    "totClimate": totalClimate
                }

                for word in masterList:
                    if word in dic:
                        yearsObj[pubDate][word] = dic[word]
                    else:
                        yearsObj[pubDate][word] = 0
        counter += 1

with open('resultYear.csv', 'w', encoding='utf-16') as f:
    headerStr = "date, total words, total climate,"
    for word in masterList:
        headerStr += word + ','
    headerStr = headerStr[:-1] # Remove last comma
    headerStr += '\n' # Complete the header line
    f.write(headerStr)

    for year in yearsObj:
        writeStr = year + ',' + str(yearsObj[year]["totWords"]) + ',' + str(yearsObj[year]["totClimate"]) + ','

        for word in masterList:
            writeStr += str(yearsObj[year][word]) + ','

        writeStr = writeStr[:-1]
        writeStr += '\n'
        f.write(writeStr)
