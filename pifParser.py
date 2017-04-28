import re
import random
import os
import subprocess
import numpy as np
import pandas as pd
import tabula
from IPython.display import HTML

def loadKeywords():
    with open('./data/keyword_fields.txt') as f:
        data = f.readlines()
        data.sort(key=len, reverse=True)
        field_regex = re.compile('|'.join([dt.replace('\n', '') for dt in data if dt != '\\w+ #\n']).replace(' ', '\s'))
        return field_regex

def dateRegex():
    date_range_regex = re.compile(r'[0-9]{2}\/[0-9]{2}\/[0-9]{2}\s*-\s*[0-9]{2}\/[0-9]{2}\/[0-9]{2}')
    date_regex = re.compile(r'[0-9]{2}\/[0-9]{2}\/[0-9]{2}')
    return date_regex, date_range_regex

def showPDF(filepath):
    return HTML('<iframe src="%s" width=1000 height=400></iframe>' % (filepath))

def doTabula(inputFile, nospreadsheet, guessArea=False, pages='all'):
    tabula.convert_into(inputFile, output_path='/tmp/convertedFCCFile.txt', output_format='csv', guess=guessArea, pages=pages, nospreadsheet=nospreadsheet)
    df = pd.read_csv('/tmp/convertedFCCFile.txt', names=range(0,7))
    return df

def readPdfToText(inputFile):
    os.system("pdftotext -layout '%s' '%s'" % (inputFile, 'test.txt'))
    pdfContent = subprocess.check_output("pdftotext -layout '%s' '%s'" % (inputFile, '-'), shell=True).decode()
    pdfLines = pdfContent.split('\n')
    df_rows = []
    for line in pdfLines:
        field_lines = [field for field in re.split('\s{2,}', line) if field != '']
        if len(field_lines) > 1:
            df_rows.append(field_lines)
    df = pd.DataFrame.from_records(df_rows)
    return df

def generateMatrixLookup(df, field_regex=loadKeywords()):
    valueMatrix = df.as_matrix()
    headerMatrix = df.applymap(lambda x: field_regex.findall(x) if type(x) == str else False).as_matrix()
    return headerMatrix, valueMatrix

def extractFields(headerMatrix, valueMatrix, extraction_method):
    extracted_fields = []
    (lx,ly) = headerMatrix.shape
    for x in range(0, lx):
        for y in range(0,ly):
            current_field = headerMatrix[x,y]
            if current_field:
                if extraction_method == 'medial' and x < lx-1:
                    target_field = valueMatrix[x+1,y]
                elif extraction_method == 'lateral' and y < ly-1:
                    target_field = valueMatrix[x,y+1]
                extracted_fields.append((current_field,target_field))
    return extracted_fields

def filterExtractedFields(extracted_fields, date_range_regex=dateRegex()[1], lazy=False):
    finalized_meta = {}
    for field, value in extracted_fields:
        if not pd.isnull(value):
            if field[0] == 'Contract / Revision' and not pd.isnull(value):
                finalized_meta['altOrder'] = value.split(' ')[0] if type(value) == str else value
            if field[0] in ['Contract Dates', 'Schedule Dates']:
                finalized_meta['flightDates'] = value
            if field[0] == 'Demographic':
                finalized_meta['Demographic'] = value
            if len(field) == 1 and field[0] == 'Advertiser':
                finalized_meta['Advertiser'] = value
            if len(field) == 1:
                if ' / ' in field[0]:
                    finalized_meta.update(dict(zip(field[0].split(' / '), value.split(' / '))))
            if len(field) > 2:
                if 'Period' in field and 'Spots' in field:
                    matched_date = date_range_regex.findall(value)[0]
                    value = value.replace(matched_date, matched_date.replace(' ', ''))
                    finalized_meta.update(dict(zip(field, value.split(' '))))
                    #if field[2] == 'Gross Amount':
                    #    finalized_meta['total'] = value.split(' ')[-1]
                #finalized_meta[field]
            if lazy:
                if len(field) == 1 and not pd.isnull(value):
                    finalized_meta[field[0].strip()] = value.strip()
    return finalized_meta

def layoutClassifier(inputFile):
    layout_regex = ['Print Date', 'Contract Agreement Between', 'Page .+ of .+', 'Remit To', 'CONTRACT NO']
    layout_meta = [
        {
            'regex': 'Contract Agreement Between',
            'nospreadsheet': False,
            'parser': 'tabula',
            'lazy': True,
            'extraction_method': 'medial'
        },
        {
            'regex': 'Page .+ of .+',
            'nospreadsheet': True,
            'parser': 'tabula',
            'lazy': True,
            'extraction_method': 'lateral'
        },
        {
            'regex': 'Print Date',
            'nospreadsheet': False,
            'parser': 'pdfToText',
            'lazy': True,
            'extraction_method': 'lateral'
        },
        {
            'regex': 'Remit To',
            'nospreadsheet': False,
            'parser': 'tabula',
            'lazy': True,
            'extraction_method': 'lateral'
        }
    ]
    layout_types = [re.compile(str.encode(t['regex'])) for t in layout_meta]
    first_line = subprocess.check_output("pdftotext -l 1 '%s' '%s' | head -n1" % (inputFile, '-'), shell=True)
    print(first_line)
    for pattern_index, pattern in enumerate(layout_types):
        if pattern.match(first_line):
            return layout_meta[pattern_index], pattern
    return None, None            
#lineMatch = re.compile(b'(Print Date)|(Contract Agreement Between)|(Page .+ of .+)|(Remit To)|(CONTRACT NO)|(Print Date)')
#for file in scanFiles('./downloads'):
#    if '.pdf' in file:
#        first_line = subprocess.check_output("pdftotext -l 1 '%s' '%s' | head -n1" % (file, '-'), shell=True)
#        if not lineMatch.match(first_line):
#           print(first_line)