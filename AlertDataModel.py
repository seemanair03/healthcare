# Check anomalies and add in alerts database
from Database import DynamoDatabase
from boto3.dynamodb.conditions import Attr
from datetime import datetime
from operator import itemgetter
import json
import os

# Load all rules from config file
with open('alerts_config.json') as configuration:
    alerts_config = json.loads(configuration.read())


class AlertsData:

    ALERTSDATA_TABLENAME = 'bsm_alerts'

    def __init__(self):
        self._db = DynamoDatabase()
        self.latest_error = ''

    #Get aggregated data to check anomalies and generate alerts
    def _get_dataset_to_process_anomaly(self, tablename, time_range_min, time_range_max):
        filter_expression = Attr('timestamp').between(time_range_min, time_range_max)
        items = self._db.read_data_for_filter(tablename, filter_expression)
        #items = self._db.read_all_data(tablename)
        itemslist = items['Items']
        itemscount = items['Count']
        #print( f'\nReceived {itemscount} aggregated records for from aggregate data table for alert processing!')
        print(
            f'\nReceived {itemscount} aggregated records for the time range from {time_range_min} to {time_range_max} from aggregate data table!')
        return itemslist


    #Get list of all anomalies
    def get_anomalies_list(self, tablename, time_range_min, time_range_max):
        anomalies = []
        anomaly = []
        agg_data_set = self._get_dataset_to_process_anomaly(tablename, time_range_min, time_range_max)
        for record in agg_data_set:
            anomaly = self.check_anomaly(record, record['min'])
            if anomaly is not None:
                anomalies.append(anomaly)
                anomaly = []
            anomaly = self.check_anomaly(record, record['max'])
            if anomaly is not None:
                anomalies.append(anomaly)
                anomaly = []
        return anomalies

    #Check if a record has an anomaly
    def check_anomaly(self, record, val):
        rule = alerts_config[record['datatype']]
        anomaly = {}
        anomaly['deviceid-datatype'] = record['deviceid'] + " " + record['datatype']
        anomaly['deviceid'] = record['deviceid']
        anomaly['datatype'] = record['datatype']
        anomaly['breach_time'] = record['timestamp']
        if (val == record['min']):
            if record['min'] < rule['avg_min']:
                alert = 'Value is below avg_min'
                anomaly['rule'] = alert
                anomaly['anomaly'] = 'min'
                return anomaly
        if (val == record ['max']):
            if record['max'] > rule['avg_max']:
                alert = 'Value is higher than avg_max'
                anomaly['rule'] = alert
                anomaly['anomaly'] = 'max'
                return anomaly


    #Generate alert if anamolies are detected consecutively at 1 min interval for a given sensor type for the trigger value configured
    def generate_alerts(self, tablename, time_range_min, time_range_max):
        alerts = []
        ctr = 0
        anomalies_list = self.get_anomalies_list(tablename, time_range_min, time_range_max)
        sorted_records = sorted(anomalies_list, key=lambda item: item.get('breach_time'), reverse=False)

        things = set(self._get_things(sorted_records))
        for thing in things:
            print(f'\nProcessing rules for device {thing}... ')
            thing_anomaly_list = []
            for i in sorted_records:
                if i['deviceid'] == thing:
                    thing_anomaly_list.append(i)

            sorted_records2 = sorted(thing_anomaly_list, key=lambda item: item.get('breach_time'), reverse=False)

            datatypes = set(self._get_datatypes(sorted_records2))
            for datatype in datatypes:
                thing_type_anomaly_list = []
                for k in sorted_records2:
                    if k['datatype'] == datatype:
                        trigger = alerts_config[k['datatype']]['trigger_count']
                        thing_type_anomaly_list.append(k)

                sorted_records3 = sorted(thing_type_anomaly_list, key=lambda item: item.get('breach_time'), reverse=False)


                sorted_records3_min = []
                for s_min in sorted_records3:
                    if s_min['anomaly'] == 'min':
                        sorted_records3_min.append(s_min)


                sorted_records3_max = []
                for s_max in sorted_records3:
                    if s_max['anomaly'] == 'max':
                        sorted_records3_max.append(s_max)



                ctr1 = 0
                first_breach_time_l = '0000-00-00 00:00:00'
                first_breach_time1 = '0000-00-00 00:00:00'
                last_breach_time1 = '0000-00-00 00:00:00'

                for l in sorted_records3_min:
                    if ctr1 < trigger:
                        if ctr1 == 0:
                            first_breach_time_l = l['breach_time']
                            first_breach_time1 = l['breach_time']
                            last_breach_time1 = l['breach_time']
                        else:
                            last_breach_time1 = l['breach_time']

                        fmt = '%Y-%m-%d %H:%M:%S'
                        tstamp1 = datetime.strptime(first_breach_time1, fmt)
                        tstamp2 = datetime.strptime(last_breach_time1, fmt)
                        td = (tstamp2 - tstamp1).total_seconds() / 60

                        if td <= 1:
                            ctr1 = ctr1+1
                            first_breach_time1 = last_breach_time1
                        elif td > 1:
                            first_breach_time1 = last_breach_time1
                            first_breach_time_l = last_breach_time1
                            ctr1 = 1


                    if ctr1 == trigger:
                        alertrecord = {}
                        alertrecord['deviceid-ruleid'] = l['deviceid'] + "-" + str(
                            self.get_rule_for_datatype(l['datatype']))
                        alertrecord['timestamp'] = first_breach_time_l
                        alertrecord['deviceid'] = l['deviceid']
                        alertrecord['ruleid'] = str(self.get_rule_for_datatype(l['datatype']))
                        alertrecord['breach_type'] = l['anomaly']
                        alerts.append(alertrecord)
                        first_breach_time_l = '0000-00-00 00:00:00'
                        first_breach_time1 = '0000-00-00 00:00:00'
                        last_breach_time1 = '0000-00-00 00:00:00'
                        ctr1 = 0


                ctr2 = 0
                first_breach_time_m = '0000-00-00 00:00:00'
                first_breach_time2 = '0000-00-00 00:00:00'
                last_breach_time2 = '0000-00-00 00:00:00'

                for m in sorted_records3_max:

                    if ctr2 < trigger:
                        if ctr2 == 0:
                            first_breach_time_m = m['breach_time']
                            first_breach_time2 = m['breach_time']
                            last_breach_time2 = m['breach_time']
                        else:
                            last_breach_time2 = m['breach_time']

                        fmt = '%Y-%m-%d %H:%M:%S'
                        tstamp1 = datetime.strptime(first_breach_time2, fmt)
                        tstamp2 = datetime.strptime(last_breach_time2, fmt)
                        td = (tstamp2 - tstamp1).total_seconds() / 60

                        if td <= 1:
                            ctr2 = ctr2 + 1
                            first_breach_time2 = last_breach_time2
                        elif td > 1:
                            first_breach_time_m = last_breach_time2
                            first_breach_time2 = last_breach_time2
                            ctr2 = 1

                    if ctr2 == trigger:
                        alertrecord = {}
                        alertrecord['deviceid-ruleid'] = m['deviceid'] + "-" + str(
                            self.get_rule_for_datatype(m['datatype']))
                        alertrecord['timestamp'] = first_breach_time_m
                        alertrecord['deviceid'] = m['deviceid']
                        alertrecord['ruleid'] = str(self.get_rule_for_datatype(m['datatype']))
                        alertrecord['breach_type'] = m['anomaly']
                        alerts.append(alertrecord)
                        first_breach_time_m = '0000-00-00 00:00:00'
                        first_breach_time2 = '0000-00-00 00:00:00'
                        last_breach_time2 = '0000-00-00 00:00:00'
                        ctr2 = 0

            alertlist = sorted(alerts, key=itemgetter('timestamp'), reverse=False)
            for alert in alertlist:
                if alert['deviceid'] == thing:
                    print(f"Alert for device_id {thing} on rule {alert['ruleid']} starting at {alert['timestamp']} with breach type {alert['breach_type']}")

            responseFlag = self._post_alert_data_to_db(thing, alerts)
            print(f'\nAcknowledged {thing} alert write to bsm_alerts with response flag {responseFlag}!')


    #Get list of all datatypes or sensors from aggregate data set
    def _get_datatypes(self, agg_data_set):
        datatypes = map(lambda ele: ele['datatype'], agg_data_set)
        return datatypes


    # Get list of all devices from raw data set
    def _get_things(self, agg_data_set):
        things = map(lambda ele: ele['deviceid'], agg_data_set)
        return things

    # Insert alerts data to bsm_alerts table in dynamo db
    def _post_alert_data_to_db(self, thing, alert_dataset):
        print(f"\nPosting data to database for device {thing}...")
        flag = self._db.insert_all_data(self.ALERTSDATA_TABLENAME, 'deviceid-ruleid', alert_dataset)
        return flag

    # Return all data from alerts data table --Currently not used from driver but provided as an extension
    def get_alerts_data(self):
        aldatacollection = self._db.read_all_data(AlertsData.ALERTSDATA_TABLENAME)
        al_data = aldatacollection['Items']
        return al_data


    #Return rule id for datatype
    def get_rule_for_datatype(self, datatype):
        config_list = alerts_config.items()
        position = 1
        for record in config_list:
            type_record = list(record)
            type = type_record[0]
            if type == datatype:
                position_val = "Rule_10" + str(position)
                return position_val
            position = position + 1


    #Writes all alerts data to a csv file
    def write_to_file(self):
        try:
            alerts_data = self.get_alerts_data()
            f_name = "alerts.csv"
            if os.path.exists(f_name):
                os.remove(f_name)
            file = open(f_name, "w")
            ctr = 1
            for record in alerts_data:
                file.write(str(ctr)+ " :"+ str(record))
                file.write("\n")
                ctr = ctr + 1
            file.close()
            print(f"\nAlerts data written to file {f_name}!")
            return True
        except Exception as e:
            print("An exception occurred ::", e)
            return False