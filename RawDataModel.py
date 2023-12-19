#Read raw_data from DynamoDB and pass data to Aggregate data model
from Database import DynamoDatabase
from boto3.dynamodb.conditions import Attr
import os


class RawData:

    RAWDATA_TABLENAME = 'bsm_data'

    def __init__(self):
        self._db = DynamoDatabase()
        self.latest_error = ''

    #Return all data from raw data table
    def get_all_raw_data(self):
        rawdatacollection = self._db.read_all_data(RawData.RAWDATA_TABLENAME)
        r_data = rawdatacollection['Items']
        return r_data

    #Return count of records in raw data table
    def get_raw_record_count(self):
        rawdatacollection = self._db.read_all_data(RawData.RAWDATA_TABLENAME)
        r_count = rawdatacollection['Count']
        return r_count


    #Read an external file on windows os
    def read_external_file(self):
        try:
            os.startfile('ACSC_OCT21_SEEMA_NAIR_PROJECT1.docx')

        except Exception as e:
            print("An exception occurred ::", e)
            return False

    #Write all raw data to a csv file
    def write_to_file(self):
        try:
            raw_data = self.get_all_raw_data()
            f_name = "rawdata.csv"
            if os.path.exists(f_name):
                os.remove(f_name)

            file = open(f_name, "w")
            ctr = 1
            for record in raw_data:
                file.write(str(ctr)+ " :"+ str(record))
                file.write("\n")
                ctr = ctr + 1
            file.close()
            print(f"\nRaw data written to file {f_name}!")
            return True
        except Exception as e:
            print("An exception occurred ::", e)
            return False

