__author__ = 'Lorenzo De Mattei'
__license__ = 'GPL'
__email__ = 'lorenzo.demattei@gmail.com'

import os
import codecs
import urllib
import urllib2
import json
import sys


def main(key, input_folder, output_folder, lang='it'):
    if not input_folder.endswith('/'):
        input_folder += '/'
    if not output_folder.endswith('/'):
        output_folder += '/'
    for bulletin in os.listdir(input_folder):
        if bulletin.endswith('.txt'):
            out = open(output_folder + bulletin[:-4] + '.json', 'w+')
            text = codecs.open('data/' + bulletin, 'r', 'utf-8-sig')
            text = text.read()
            url = 'http://tagme.di.unipi.it/tag'
            values = {'key': key,
                      'text': text.encode('utf-8'),
                      'lang': lang,
                      'include_abstract': 'true',
                      'include_categories': 'true'}

            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            entities = response.read()

            out.write(json.dumps(entities, sort_keys=True, indent=5, encoding='utf8'))
            out.close()

if __name__ == '__main__':
    try:
        main(sys.argv[1], sys.argv[2], sys.argv[3], lang=sys.argv[4])
    except IndexError:
        main(sys.argv[1], sys.argv[2], sys.argv[3])