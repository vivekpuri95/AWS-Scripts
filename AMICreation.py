import boto3, datetime
from datetime import date
from datetime import datetime
from botocore.exceptions import ClientError

application-server = {
    'prefix': "ApplicationServer-LiveAMI", # Name of AMI
    'InstanceID': "<on-demand-instance-id>",
    'Region': "<on-demand-instance-region>",
    'delBefore': 2 # Number of AMIs to keep
    }
strOfObjs = [application-server]

def createAMI(name, InstanceID,ec2):
    try:
        ec2.create_image(InstanceId=InstanceID, Name=name,NoReboot=True)
    except ClientError as e:
        print("Error creating AMI for "+ name)
        print(e.response['Error']['Message'])
        return ("Error creating AMI for "+ name)
    else:
        print("creating AMI for "+ name)
        return(name)

def lambda_handler(event, context):
    for i in strOfObjs:
        prefix = i['prefix']
        InstanceID = i['InstanceID']
        Region = i['Region']
        delBefore = i['delBefore']
        today = date.today()
        date_format = "%Y/%m/%d"
        today=today.strftime('%Y/%m/%d')
        a = datetime.strptime(today, date_format)
        time = datetime.now()
        name = prefix + time.strftime("-%Y%m%d%H%M")
        ec2 = boto3.client('ec2', region_name = Region)
        result = createAMI(name, InstanceID, ec2)
        createList.append(result)
        images=ec2.describe_images(Owners=['self'])
        for currImage in images['Images']:
            if currImage['Name'].startswith(prefix):
                amiId=currImage['ImageId']
                creationDate=currImage['CreationDate']
                creationDate=creationDate[:10]
                creationDate=creationDate.replace("-", "/")
                b = datetime.strptime(creationDate, date_format)
                diff = a-b
                if diff.days > delBefore:
                    print("\tRemoving Image:"+currImage['Name'])
                    deleteList.append(currImage['Name'])
                    ec2.deregister_image(ImageId=amiId)
                    blockDevices = currImage['BlockDeviceMappings']
                    for currBlock in blockDevices:
                        if 'SnapshotId' in currBlock['Ebs']:
                            snapId = currBlock['Ebs']['SnapshotId']
                            ec2.delete_snapshot(SnapshotId=snapId)
