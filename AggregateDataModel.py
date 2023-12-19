#Aggregates raw data and put in aggregate database
from Database import DynamoDatabase
from boto3.dynamodb.conditions import Attr
from time import strptime
from datetime import datetime
import pandas as pd
import math
import os

class AggregateData:

    AGGDATA_TABLENAME = 'bsm_agg_data'

    def __init__(self):
        self._db = DynamoDatabase()
        self.latest_error = ''

    #Aggregate raw data and posts to database
    def aggregate_data(self, tablename, time_range_min, time_range_max):
        raw_dataset = self._get_dataset_to_aggredate(tablename, time_range_min, time_range_max)
        things = set(self._get_things(raw_dataset))
        for thing in things:
            print(f"\nAggregating data for device {thing}")
            aggregated_data = self._process_rawdataset(thing,raw_dataset)
            responseFlag = self._post_aggregated_data_to_db(thing, aggregated_data)
            print(f'\nAcknowledged {thing} aggregate write to bsm_agg_table with response flag {responseFlag}!')

    #Get data for given timerange from raw data table to aggregate
    def _get_dataset_to_aggredate(self, tablename, time_range_min, time_range_max):
        filter_expression = Attr('timestamp').between(time_range_min, time_range_max)
        items = self._db.read_data_for_filter(tablename, filter_expression)
        itemslist = items['Items']
        itemscount = items['Count']
        print( f'\nReceived {itemscount} raw records for the time range from {time_range_min} to {time_range_max} from raw data table!')
        return itemslist

    #Insert aggregated data to bsm_agg_data table in dynamo db
    def _post_aggregated_data_to_db(self, thing, aggregated_dataset):
        print(f"\nPosting data to database for device {thing}...")
        flag = self._db.insert_all_data(self.AGGDATA_TABLENAME, 'deviceid-datatype', aggregated_dataset)
        return flag


    #Get list of all devices from raw data set
    def _get_things(self, raw_data_set):
        things = map(lambda ele: ele['deviceid'], raw_data_set)
        return things

    #Process the raw data set and returns aggregate data for a given device
    def _process_rawdataset(self, thing, raw_data_set):
        thing_agg_data_list = []
        thing_data_set = []
        for record in raw_data_set:
            if thing == record['deviceid']:
                thing_data_set.append(record)
        df = pd.DataFrame(thing_data_set)
        df['timestamp'] = pd.to_datetime(df.timestamp, format='%Y-%m-%d %H:%M')
        agg_d = df.groupby(['deviceid', 'datatype', pd.Grouper(key='timestamp', freq='1min')], as_index=False).agg(
            ['mean',  'min', 'max']).reset_index()

        agg_d['value'] = agg_d['value'].astype(int)
        agg_d['deviceid-datatype'] = agg_d.deviceid + "-" + agg_d.datatype

        agg_d['timestamp'] = agg_d['timestamp'].astype(str)

        agg_d_o = pd.DataFrame(agg_d)

        thing_dict = agg_d_o.to_dict('records')
        thing_agg_data_list = list(thing_dict)

        for record in thing_agg_data_list:

            oldkey1 = list(record.keys())[0]
            newkey1 = 'deviceid'
            record[newkey1] = record.pop(oldkey1)

            oldkey2 = list(record.keys())[0]
            newkey2 = 'datatype'
            record[newkey2] = record.pop(oldkey2)

            oldkey3 = list(record.keys())[0]
            newkey3 = 'timestamp'
            record[newkey3] = record.pop(oldkey3)

            oldkey4 = list(record.keys())[0]
            newkey4 = 'avg'
            record[newkey4] = record.pop(oldkey4)

            oldkey5 = list(record.keys())[0]
            newkey5 = 'min'
            record[newkey5] = record.pop(oldkey5)

            oldkey6 = list(record.keys())[0]
            newkey6 = 'max'
            record[newkey6] = record.pop(oldkey6)

            oldkey7 = list(record.keys())[0]
            newkey7 = 'deviceid-datatype'
            record[newkey7] = record.pop(oldkey7)

        return thing_agg_data_list

    #Return all data from aggregate data table
    def get_aggregated_data(self):
        adatacollection = self._db.read_all_data(AggregateData.AGGDATA_TABLENAME)
        a_data = adatacollection['Items']
        return a_data

    #Return count of records in aggregae data table
    def get_aggregated_record_count(self):
        aggdatacollection = self._db.read_all_data(AggregateData.AGGDATA_TABLENAME)
        a_count = aggdatacollection['Count']
        return a_count

    #Write all aggregate data to a csv file
    def write_to_file(self):
        try:
            agg_data = self.get_aggregated_data()
            f_name = "aggregateddata.csv"
            if os.path.exists(f_name):
                os.remove(f_name)

            file = open(f_name, "w")
            ctr = 1
            for record in agg_data:
                file.write(str(ctr)+ " :"+ str(record))
                file.write("\n")
                ctr = ctr + 1
            file.close()
            print(f"\nAggregated data written to file {f_name}!")
            return True
        except Exception as e:
            print("An exception occurred ::", e)
            return False