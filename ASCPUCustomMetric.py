import boto3
import sys
from datetime import datetime, timedelta
from operator import itemgetter

def lambda_handler(event, context):
    now = datetime.utcnow()
    past = now - timedelta(minutes=10)
    future = now + timedelta(minutes=10)
    ec2client = boto3.client('ec2')
    cwclient = boto3.client('cloudwatch')
    custom_filter = [{
        'Name':'tag:AppASLive', 
        'Values': ['true']}]
    instances = ec2client.describe_instances(Filters=custom_filter)
    TotalCPU = 0
    count = 0
    for instance in instances['Reservations']:
        for instanceid in instance['Instances']:
            if instanceid['State']['Name'] == "running" :
                try :
                    results = cwclient.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[
                        {
                        'Name': 'InstanceId',
                        'Value': instanceid['InstanceId']
                        },
                    ],
                    StartTime=past,
                    EndTime=future,
                    Period=60,
                    Statistics=[
                        'Average',
                    ],
                    Unit='Percent'
                    )
                    datapoints = results['Datapoints']
                    last_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))[-1]
                    utilization = last_datapoint['Average']
                    count+=1
                except:
                    utilization=0
                    
                TotalCPU += utilization
    try:
        AvgCPU = TotalCPU/count
        response = cwclient.put_metric_data(
            Namespace='AppASLive',
            MetricData=[
                {
                    'MetricName': 'AverageCPUUtilization',
                    'Dimensions': [
                        {
                            'Name': 'CPUUtilization',
                            'Value': 'AppASLiveCPU'
                        },
                    ],
                    'Value': AvgCPU,
                    'Unit': 'Percent'
                },
            ]
        )
    except:
        print "No instances found with above mentioned Tag"
