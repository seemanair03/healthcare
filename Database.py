#Contains Constructor class for inserting to and reading from dynamoDB database
import boto3
from decimal import Decimal
import json

class DynamoDatabase:

    def __init__(self):
        self._dynamodb = boto3.resource('dynamodb')

    #Return all data from the given table
    def read_all_data(self, tablename):
        try:
            bsm_table = self._dynamodb.Table(tablename)
            response = bsm_table.scan()
            response['Items']
            return response
        except Exception as e:
            print("An exception occurred ::", e)
            return False

    #Return data from the given table for specified filter query
    def read_data_for_filter(self, tablename, filterquery):
        try:
            bsm_table = self._dynamodb.Table(tablename)
            response = bsm_table.scan(FilterExpression=filterquery)
            response['Items']
            #print (response)
            return response
        except Exception as e:
            print("An exception occurred ::", e)
            return False

    #Post all data to given table
    def insert_all_data(self, tablename, pk, data_set):
        #try:

        bsm_table = self._dynamodb.Table(tablename)
        with bsm_table.batch_writer(overwrite_by_pkeys=[pk, 'timestamp']) as batch:
           for record in data_set:
                if record is not None:
                    batch.put_item(Item=record)
        return True
        #except Exception as e:
            #print("An exception occurred ::", e)
            #return False