#### PDF Parser
import requests
import PyPDF2
import io
import os
import re

class ReportPDFReader:
    def __init__(self):
        self.reader = None
        self._default_path = '.'
        self._file_path = None
        self._file_name = None

    def read_from_url(self, url:str, read:bool = True):
        r = requests.get(url)
        if (r.status_code != 200):
            raise ConnectionError('URLcontaing pdf:{} not connectable or not a pdf'.format(url))
        self._file_path = url
        self._file_name = url.split('/')[-1]

        if (not read):
            del r
            return self
        
        f = io.BytesIO(r.content)
        self.reader = PyPDF2.PdfFileReader(f)
        del f, r
        return self

    def key_exist(self, key:str)->bool:
        if (self.reader == None):
            return False
        for i in range(self.reader.getNumPages()):
            page_text = ''.join(self.reader.getPage(i).extractText())
            if key.lower() in page_text.lower():
                return True
        return False

    def save_from_pdf(self, file_name:str):
        writer = PyPDF2.PdfFileWriter()
        writer.appendPagesFromReader(self.reader)

        with open(file_name, 'wb') as f:
            writer.write(f)
            f.close()
    
    def save_from_link(self, file_name:str):
        r = requests.get(self._file_path, allow_redirects = True)
        
        with open(file_name, 'wb') as f:
            f.write(r.content)
            f.close()
    
    def save(self, dest:str)->bool:
        out_file = ''
        if (not os.path.isdir(dest)):
            dest = self._default_path
        out_file = (dest + os.path.sep + self._file_name)

        if (self.reader != None):
            self.save_from_pdf(out_file)
            return True
        
        elif (self._file_path != None):
            self.save_from_link(out_file)
            return True
        else:
            print('No PDF file can be saved.')
            return False


if __name__ == '__main__':
    url = 'https://www.accessdata.fda.gov/cdrh_docs/pdf19/K191323.pdf'
    test = ReportPDFReader()
    test.read_from_url(url)
    while(True):
        key = input('Enter search key (enter nothing to leave):')
        if (key == ''):
            break
        print('Is {} existed in pdf? {}'.format(key, test.key_exist(key)))

    print('File Saved:', test.save('.'))