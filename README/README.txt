
----------------------------------------------README--------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------

The project executes successfully only after all the required setup is done on AWS, as detailed below STEPS

--------------------------------------------------------------------------------------------------------------------
STEP 1).    From AWS IAM UI - Create IAM Role (for project created role = 'bsm_role_seema')
--------------------------------------------------------------------------------------------------------------------
STEP 2).    From AWS IoT Core UI - Create Type (for project created type = 'BSM_SN')
--------------------------------------------------------------------------------------------------------------------
STEP 3).    From AWS IoT Core UI - Create Group (for project created group = 'Hospital')
--------------------------------------------------------------------------------------------------------------------
STEP 4).    From AWS IoT Core UI - Create Policy (for project created policy = 'bsm_policy')
--------------------------------------------------------------------------------------------------------------------
STEP 5).    From AWS IoT Core UI - Create Things (for project created things = 'BSM_G101', 'BSM_G102')
--------------------------------------------------------------------------------------------------------------------
STEP 6).    While creating things at STEP 4 download the certificates and keys
            and save in same folder as project files. Also copy the endpoint.
            Remember to rename the root certificates to avoid conflict for the two things.

            Command Format:
            python BedSideMonitor1.py
            -e endpoint
            -r Root_certificate
            -c Thing_certificate
            -k Thing_private_key
            -id clientid
            -t topic_name

            Here are the commands (remember this will change when new things are created)

            For Command Window1
            python BedSideMonitor1.py -e a3fhbju8xoji12-ats.iot.us-east-1.amazonaws.com -r AmazonRootCA1_1.pem
            -c 2c1f7cb5d75174707ae08bdb718bc986a2b870afcc05138b2fbc28f5c1e9fe20-certificate.pem.crt
            -k 2c1f7cb5d75174707ae08bdb718bc986a2b870afcc05138b2fbc28f5c1e9fe20-private.pem.key
            -id BSM_G101 -t hospital/bangalore/bsm_g101

            For Command Window2
            python BedSideMonitor2.py -e a3fhbju8xoji12-ats.iot.us-east-1.amazonaws.com -r AmazonRootCA1_2.pem
            -c 4b13711276e5db9fc94414e3915a403442549a4da931db15b4af4e3d94e680d2-certificate.pem.crt
            -k 4b13711276e5db9fc94414e3915a403442549a4da931db15b4af4e3d94e680d2-private.pem.key
            -id BSM_G102 -t hospital/bangalore/bsm_g102
--------------------------------------------------------------------------------------------------------------------
 STEP 7).   From AWS DynamoDB UI - Create 3 dynamoDB tables:-
            A. bsm_data: to hold the raw_data (partitian key = deviceid, sort key = timestamp)
            B. bsm_agg_data: to hold the aggregate_data (partitian key = deviceid-datatype, sort key = timestamp)
            C. bsm_alerts: to hold the anomaly_data (partitian key = deviceid-ruleid, sort key = timestamp)
--------------------------------------------------------------------------------------------------------------------
 STEP 8).   From AWS IoT Core UI - Create MQTT Test Subscriptions for two topics
            A.  hospital/bangalore/bsm_g101
            B.  hospital/bangalore/bsm_g102
--------------------------------------------------------------------------------------------------------------------
 STEP 9).   From AWS IoT Core UI - Create two Rules for raw data population to bsm_data table
            (for project created rules = 'BSM_Device1', 'BSM_Device2')
--------------------------------------------------------------------------------------------------------------------
 STEP 10).  Open two command windows, and on both go to project folder.
--------------------------------------------------------------------------------------------------------------------
 STEP 11).  Execute Command from STEP 6
            A. For Command Window1 on Command Window1
            B. For Command Window2 on Command Window2
--------------------------------------------------------------------------------------------------------------------
 STEP 12).  VALIDATION - From AWS IoT Core UI - Check MQTT Test on the two subscriptions (from STEP 8)
--------------------------------------------------------------------------------------------------------------------
 STEP 13).  VALIDATION - From AWS DynamoDB UI - Check bsm_data table.
            Refresh the table to see the raw data getting posted from both the things BSM_G101 & BSM_G102
--------------------------------------------------------------------------------------------------------------------
 STEP 14).  Let STEP 11 continue to run for > 1 hour duration.
--------------------------------------------------------------------------------------------------------------------
 STEP 15).  After > 1 of STEP 14, run Main.py file in project folder
            (...\C04P01-Project-HealthCare-IoT-Cloud_SeemaNair_V1\C04P01-Project-HealthCare-IoT-Cloud\Main.py)
--------------------------------------------------------------------------------------------------------------------
 STEP 16).  VALIDATION -  After Main.py program executes successfully from STEP 15
            A. From AWS IoT Core UI - Check bsm_agg_data table
            B. From AWS IoT Core UI - Check bsm_alerts table
--------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------
SCREENSHOTS:
Check
...\C04P01-Project-HealthCare-IoT-Cloud_SeemaNair_V1\C04P01-Project-HealthCare-IoT-Cloud\ACSC_OCT21_SEEMA_NAIR_PROJECT1.docx
for screenshots (C04P01-IoT-HealthCare-Cloud-Workbook.docx was renamed to ACSC_OCT21_SEEMA_NAIR_PROJECT1.docx)

NOTE1:   Kindly note that the data on some screenshots are from different dates/times,
        so it might not all match up to be a single project session.


NOTE2:   This submission is considering the alert logic to be -- agg_min < avg_min or agg_max > avg_max, then raise alert.	

-----------------------------------------END OF README--------------------------------------------------------------





