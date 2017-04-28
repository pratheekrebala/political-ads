import requests
import json
from urllib.request import urlretrieve
import urllib.parse as urlparse
import os

all_docs = []
downloadedDocs = 0
totalDocs = 0

def queryOPIF(offset=0):
    fcc_url = 'https://www.fcc.gov/search/api'
    atlanta_filters = json.dumps([{'nielsen_dma_rank':'ATLANTA', 'campaign_year':'2017'}])
    payload = {'t': 'opif', 'q':'!disclosure AND !nab', 's':offset, 'o':'best', 'f':atlanta_filters}
    r = requests.get(fcc_url, params=payload)
    results = r.json()
    if results['responseStatus']['status'] == 200:
        totalDocs = results['response']['numFound']
        return totalDocs,results
    else: print(results)

def downloadFile(reqUrl, downloadPath=None):
    dlUrl = 'https://publicfiles.fcc.gov/api'
    if not downloadPath:
        downloadPath = './downloads/'
    file_path = os.path.basename(urlparse.urlparse(reqUrl).path)
    return dlUrl + reqUrl
    #return urlretrieve(dlUrl + reqUrl, downloadPath +file_path)


def download(file):
        '''
        Download a political file.
        https://publicfiles.fcc.gov/api/manager/download/d51881d5-fe65-e976-81ee-3e5a626aaee6/7a21d601-1c1c-41b4-b8f2-a22dca06cade.pdf
        :param self:
        :return:
        '''
        folder_id = file['folder_id']
        file_manager_id = file['file_manager_id']
        file_name = file['file_name']
        if 'NAB' not in file_name:
            entityUrl = '/manager/download/{folder_id}/{file_manager_id}.pdf'.format(folder_id=folder_id, file_manager_id=file_manager_id)
            print(entityUrl)
            return downloadFile(entityUrl)

while downloadedDocs == 0 or downloadedDocs < totalDocs:
    totalDocs, results = queryOPIF(downloadedDocs)
    docs = [doc for doc in results['response']['docs']]
    currentSize = len(docs)
    all_docs.extend(docs)
    downloadedDocs += currentSize
    print('Found %d documents of %d documents. ' % (downloadedDocs, totalDocs))

thefile = open('downloads.txt', 'w')
for item in [download(doc) for doc in all_docs]:
      thefile.write("%s\n" % item)
    #print(results['response']['docs'])
#print(len([doc['id'] for doc in results['response']['docs']]))