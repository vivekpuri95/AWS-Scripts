import boto3
from datetime import date
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    prefix = "ApplicationServer-LiveAMI"
    Region = "<launch-template-region>"
    launchTemplate = '<launch-template-id>'
    ec2 = boto3.client('ec2', region_name = Region)
    
    #get AMI IDs by prefix and import time string as datetime object
    try:
    	images=ec2.describe_images(Owners=['self'])
    except:
    	print "Error getting current images"
    
    amiList=[]
    for currImage in images['Images']:
    	if currImage['Name'].startswith(prefix):
    		amiList.append({'ImageId':currImage['ImageId'],'CreationDate':datetime.strptime(currImage['CreationDate'], '%Y-%m-%dT%H:%M:%S.000Z')}) 
    		
    #sort AMI Id's by date
    amiList.sort(key=lambda x: x['CreationDate'],reverse=True)
    #ami id of latest AMI
    amiID=amiList[0]['ImageId']
    
    #get Version for default launchTemplate
    try:
    	describe_template_response = ec2.describe_launch_template_versions(LaunchTemplateId=launchTemplate,Filters=[{'Name':'is-default-version','Values':['true']}])
    except:
    	print "Error getting default version number for template"
    defaultVersionNumber = describe_template_response['LaunchTemplateVersions'][0]['VersionNumber']
    
    #create new templateversion with latestversion and 
    try:
    	create_template_response = ec2.create_launch_template_version(LaunchTemplateId=launchTemplate,VersionDescription=amiID,SourceVersion=str(defaultVersionNumber),LaunchTemplateData={'ImageId':amiID})
    except:
    	print "Error creating new launch tempate"
    newVersionNumber = create_template_response['LaunchTemplateVersion']['VersionNumber']
    
    #set new version as default
    try:
    	modify_template_response = ec2.modify_launch_template(LaunchTemplateId=launchTemplate,DefaultVersion=str(newVersionNumber))
    except:
    	print "Error setting new version as default"
