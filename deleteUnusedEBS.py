import boto3
ec2 = boto3.resource('ec2',region_name='us-east-1')
ec2snap = boto3.client('ec2')
def lambda_handler(event, context):
# Get all in-use volumes in all regions  
	result = ec2snap.describe_volumes( Filters=[{'Name': 'status', 'Values': ['available']}])

	for volume in result['Volumes']:
		print("Backing up %s in %s" % (volume['VolumeId'], volume['AvailabilityZone']))
		volumeId = volume['VolumeId']
		
		# Find name tag for volume if it exists
		if 'Tags' in volume:
			for tags in volume['Tags']:
				if tags["Key"] == 'snapshotCreated':
					snapCreate = tags["Value"]
# Create snapshot
		if snapCreate != 'True':
			result = ec2snap.create_snapshot(VolumeId=volume['VolumeId'],Description='Created by Lambda backup function ebs-snapshots')
			ec2snap.create_tags(Resources=[
        	volume['VolumeId'],
    	],
    	Tags=[
        	{
           		'Key': 'snapshotCreated',
           		'Value': 'True',
        	},
    	],)
			print("Snapshot created and Tag added to volume")
 
 #Delete Volumes ref: https://github.com/tprakash17/Lambda-delete-unused-EBS/blob/master/lambda-function-delete-EBS.py
	for vol in ec2.volumes.all():
			if  vol.state=='available' and vol.tags is not None:
				for tag in vol.tags:
						if tag['Key'] == 'DoNotDelete':
							value=tag['Value']
							if value != 'DND' and vol.state=='available':
								vid=vol.id
								v=ec2.Volume(vol.id)
								v.delete()
								print("Deleted available volume with no DND tag:" +vid)
						else:
							if vol.state=='available':
								vid=vol.id
								v=ec2.Volume(vol.id)
								v.delete()
								print("Deleted available volume with no DND tag:" +vid)
			elif vol.tags is None and vol.state=='available':
				vid=vol.id
				v=ec2.Volume(vol.id)
				v.delete()
				print("Deleted available volume with no tags:" +vid)
				continue
			else:
				if vol.state=='available':
					vid=vol.id
					v=ec2.Volume(vol.id)
					v.delete()
					print("Deleted available volume:" +vid)
