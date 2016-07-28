import os
import osc.importer.inforiego as inforiego
import osc.importer.sigpac as sigpac
import sys

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
err_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'handlers')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')
# encoding = 'mbcs'
encoding = 'iso-8859-1'

if __name__ == "__main__":
    module = sys.argv[1]

    if module == 'inforiego':
        for y in sys.argv[2:]:
            year = str(y)

            print 'Importing ' + year

            inforiego.save2elasticsearch(years=[year],
                                         data_dir=data_dir,
                                         encoding=encoding,
                                         tmp_dir=tmp_dir)
    elif module == 'SIGPAC':
        for zc in sys.argv[2:]:
            zip_code = str(zc)

            print 'Importing ' + zip_code

            sigpac.save2elasticsearch(zip_codes=sigpac.all_zipcodes(starting_with=zip_code))

