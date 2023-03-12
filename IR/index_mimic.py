Max_Rows = 1000

import sys, os,lucene, threading, time, psycopg2
from datetime import datetime
from configparser import ConfigParser

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import FSDirectory


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):

    def __init__(self, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        self.conn = None

        store = FSDirectory.open(Paths.get(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocsFromDB(writer)
        ticker = Ticker()
        print ('commit index\n',)
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        store.close()
        ticker.tick = False
        print ('done\n')

    def connectToDatabase(self):
        self.conn = None
        self.conn = psycopg2.connect(host="172.16.34.1", port="5432", database="mimic", user="mimic_demo", password="mimic_demo")


    def indexDocsFromDB(self, writer):
        self.connectToDatabase()
        cursor = self.conn.cursor()

        if not cursor : return False

        note_id = FieldType()
        note_id.setStored(True)
        note_id.setTokenized(False)
        note_id.setIndexOptions(IndexOptions.DOCS_AND_FREQS) 

        chartdate = FieldType()
        chartdate.setStored(True)
        chartdate.setTokenized(True)
        chartdate.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        hospital_expire_flag = FieldType()
        hospital_expire_flag.setStored(True)
        hospital_expire_flag.setTokenized(False)
        hospital_expire_flag.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        category = FieldType()
        category.setStored(True)
        category.setTokenized(False)
        category.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        hadm_id = FieldType()
        hadm_id.setStored(True)
        hadm_id.setTokenized(False)
        hadm_id.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        icd9_code = FieldType()
        icd9_code.setStored(True)
        icd9_code.setTokenized(True)
        icd9_code.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        text = FieldType()
        text.setStored(True)
        text.setTokenized(True)
        text.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        query =('select n.row_id note_id,to_char(n.chartdate, \'YYYY-MM-DD\') chartdate, a.hospital_expire_flag,n.category,a.hadm_id,n.text '
            'from mimiciii.admissions a,mimiciii.noteevents n where a.hadm_id=n.hadm_id and n.category=\'Discharge summary\' ')
        query += ' limit '+ str(Max_Rows)
        cursor.execute(query)
        rows = cursor.fetchall()
        i = 0
        for row in  rows:
            doc = Document()
            doc.add(Field("note_id", str(row[0]), note_id))
            doc.add(Field("chartdate", str(row[1]) if row[1] else '', chartdate))
            doc.add(Field("hospital_expire_flag", str(row[2]), hospital_expire_flag))
            doc.add(Field("category", row[3], category))
            doc.add(Field("hadm_id", str(row[4]), hadm_id))
            doc.add(Field("text", row[5], text))
            query1 = ('select i.icd9_code, i.short_title  from  mimiciii.diagnoses_icd d, mimiciii.d_icd_diagnoses i '
                        ' where d.icd9_code = i.icd9_code and hadm_id = ')
            query1 += str(row[4])
            cursor.execute(query1)
            rows_of_icd9 = cursor.fetchall()
            icd9_result = ''
            for row_of_icd9 in rows_of_icd9:
                icd9_result +=str(row_of_icd9[0]) +','+ str(row_of_icd9[1])
                doc.add(Field("icd9_code", icd9_result, icd9_code))
                i += 1
                if (i % 100 == 0): 
                    writer.addDocument(doc)

        self.conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Index folder path is required. For example:")
        print("python index_mimic.py mimiciii.Index")
        sys.exit(1)

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    
    print('Indexing...', datetime.now())
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    IndexFiles(sys.argv[1], StandardAnalyzer())
    print('Indexing finished. ', datetime.now())



