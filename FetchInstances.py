import boto3,datetime,filecmp,os
from shutil import copyfile
from shutil import move
ec2client=boto3.client('ec2')
asclient = boto3.client('autoscaling')
count,servers = 3,[]
dt = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
filename = "haproxy.cfg-" + dt
copyfile("haproxy.tmpt", filename)
f = open(filename, 'a')
response = asclient.describe_auto_scaling_groups(AutoScalingGroupNames=['AppASLive'])['AutoScalingGroups']
for instance in response:
    for id in instance['Instances']:
        if id['LifecycleState'] == "InService" :
            ip = ec2client.describe_instances(InstanceIds=[id['InstanceId']])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
            servers.append(ip)
            f.write("server web" + str(count) + " " + ip + ":8888 check fall 4 rise 2\n") # My application is running on port 8888
            count+=1
f.close()
difference=filecmp.cmp('haproxy.cfg', filename)
print difference
if filecmp.cmp('haproxy.cfg', filename):
    os.remove(filename)
else:
    command = "/usr/sbin/haproxy -f " + filename + " -c"
    confcheck = os.system(command)
    if confcheck == 0 :
        try:
            move("haproxy.cfg","backup/haproxy.cfg-"+dt)
            move(filename, "haproxy.cfg")
            os.system("service haproxy reload")
        except:
            print "Error moving haproxy.cfg to backup folder"
