#Main driver program
from RawDataModel import RawData
from  AggregateDataModel import AggregateData
from  AlertDataModel import AlertsData
import os

raw_data = RawData()
agg_data = AggregateData()
alerts_data = AlertsData()

print("\n ---------------PROBLEM STATEMENT 1 - C04P01 - IoT - HealthCare - Cloud - Workbook ---------------")

#Check if user wants to view the raw data generation steps
check_flag = input("\nDo you want to view the file with details on raw data generation? Yes/No: ")


if check_flag == "Yes" or check_flag == "yes":
    print("\n WARNING: Word should be installed on the Windows Machine for this step to work successfully")
    print("\n --------------- Opening ACSC_OCT21_SEEMA_NAIR_PROJECT1.docx on Windows OS ---------------")
    raw_data.read_external_file()

#Prints count of all raw data in raw data database
print("\n ---------------Getting raw data from database ---------------")
raw_data_count = raw_data.get_raw_record_count()
print(f'\nTotal raw data records {raw_data_count}')

#Check if user wants the raw data written to an output file
write_raw_flag = input("Do you want to write raw data to file? Yes/No: ")

if write_raw_flag == "Yes" or write_raw_flag == "yes":
    print("\n ---------------Writing raw data to file---------------")
    raw_data.write_to_file()

print("\n ---------------PROBLEM STATEMENT 2 - Aggregate the data in another table ---------------")


#Provide time range to filter data for aggregation
print("\n ---------------Getting Timerange for aggregation---------------")

timerangemin = input("Enter start time for analysis, e.g. 2022-03-29 15:19:00.000000: ")
timerangemax = input("Enter end time for analysis, e.g. 2022-03-29 16:19:00.000000: ")
print("WARNING: If you do not get any records for expected data in timerange, "
      "please check the format and try again! (try copy-pasting format from given example and change values)")

#Aggregates data and posts to aggregregate data table
print("\n ---------------Aggregating Raw Data ---------------")
adata = agg_data.aggregate_data(raw_data.RAWDATA_TABLENAME, str(timerangemin), str(timerangemax))
print("\n ---------------Getting aggregated data from database ---------------")
aggdatacount = agg_data.get_aggregated_record_count()
print(f'\nTotal aggregated data records {aggdatacount}')


#Check if user wants the aggregated data written to an output file
write_agg_flag = input("\nDo you want to write aggregated data to file? Yes/No: ")

if write_agg_flag == "Yes" or write_agg_flag == "yes":
    print("\n ---------------Writing aggregated data to file---------------")
    agg_data.write_to_file()

print("\n ----------PROBLEM STATEMENT 3 - Detect anomalies for a time range based on rules and store them ---------------")


#Provide time range to filter data for checking anomalies
print("\n ---------------Getting Timerange for anomalies---------------")

timerangemin = input("Enter start time for analysis, e.g. 2022-03-29 15:19:00.000000: ")
timerangemax = input("Enter end time for analysis, e.g. 2022-03-29 16:19:00.000000: ")
print("WARNING: If you do not get any records for expected data in timerange, "
      "please check the format and try again! (try copy-pasting format from given example and change values)")


print("\n ---------------Checking Anomalies, generating alerts and posting Alerts to database---------------")
alerts_data.generate_alerts(agg_data.AGGDATA_TABLENAME, timerangemin, timerangemax )


#Check if user wants the alerts data written to an output file
write_alerts_flag = input("\nDo you want to export alerts data to file? Yes/No: ")

if write_alerts_flag == "Yes" or write_alerts_flag == "yes" :
    print("\n ---------------Writing aggregated data to file---------------")
    alerts_data.write_to_file()


print("\n ---------------'Thank You!' ---------------")
print("\n ----------------THE END -------------------")





