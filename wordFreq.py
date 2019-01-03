import re
import string
import os

def parseBook(inputFile):
    bookFile = open(inputFile, 'r', encoding='utf-16') # Establish a file reader
    book = bookFile.read() # Read the file
    bookWithoutPunctuation = book.translate(str.maketrans('','',string.punctuation)) # Get rid of punctuation
    bookWithoutNumbers = bookWithoutPunctuation.translate(str.maketrans('','',string.digits))
    bookList = re.split(' |\r\n|\n', bookWithoutNumbers) # Split by space or newline
    bookListWithoutEmpty = list(filter(None, bookList)) # Remove empty elements
    cleanBook = map(lambda word: word.lower(), bookListWithoutEmpty) # Convert all letters to lowercase
    return list(cleanBook)

wordFile = open('Word-list.txt', 'r', encoding='utf-16')
masterList = list(map(lambda word: word.strip().lower(), wordFile.read().split(',')))

with open('results.csv', 'w', encoding='utf-16') as f:
    for filename in os.listdir(os.getcwd() + '/books'):
        print(filename)
        dict = {} # Establish a dictionary
        wordList = parseBook('books/' + filename)
        print(wordList)
        for word in wordList:
            if word in dict:
                dict[word] = dict[word] + 1
            else:
                dict[word] = 1

        f.write('\n' + filename + ',' + str(len(wordList)) + '\n')
        for word in masterList:
            if word in dict:
                f.write(word + ',' + str(dict[word]) + '\n')
            else:
                f.write(word + ',0\n')
