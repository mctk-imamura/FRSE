# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
import os

def file2dic(file_path):
    book = {'content':''}
    with open(file_path, 'rt', encoding = "sjis") as f:
        state = 'header'
        for line in f:
            if state == 'header':
                if line.startswith('Title: '):
                    book['title'] = line.split(':')[1].strip()
                elif line.startswith('Country: '):
                    book['country'] = line.split(':')[1].strip()
                elif line.startswith('Number: '):
                    book['number'] = line.split(':')[1].strip()
                elif line.startswith('Source: '):
                    book['source'] = line.split(':')[1].strip()
                elif line.startswith('Organization: '):
                    book['organization'] = line.split(':')[1].strip()
                elif line.startswith('Path: '):
                    book['path'] = line.split(' ')[1]
                elif line.startswith('*** START '):
                    state = 'body'
            elif state == 'body':
                if line.startswith('*** END '):
                    break
                book['content'] += line
    return book

path = 'C:\\Users\\mctki\\Desktop\\2.txt'
book = file2dic(path)
_id = os.path.splitext(os.path.basename(path))[0]

print(book['content'])

es = Elasticsearch()

es.index(index='fuel_research', doc_type='_doc', id=_id, body=book)
