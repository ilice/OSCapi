import os
import osc.importer.inforiego as inforiego
import sys

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
err_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'handlers')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')
# encoding = 'mbcs'
encoding = 'iso-8859-1'

if __name__ == "__main__":
    for y in sys.argv[1:]:
        year = str(y)

        print 'Importing ' + year

        inforiego.save2elasticsearch(years=[year],
                                     data_dir=data_dir,
                                     encoding=encoding,
                                     tmp_dir=tmp_dir)
