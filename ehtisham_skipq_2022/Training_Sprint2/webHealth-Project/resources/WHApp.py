import urllib3, datetime
from cloudWatch_putData import AWSCloudWatch

import constants as constants

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data

def lambda_handler(event, context):
    cloudwatch_object = AWSCloudWatch()
    # client = boto3.client('cloudwatch')
    
    #Executing functions to fetch website active status and latency 
    values=dict()
    availability=getAvail()
    latency=getLatency()
    values.update({"availability":availability, "latency":latency})
    
    # sending data to cloudWatch
    dimensions=[{'Name':'URL', 'Value':constants.url}]
    cloudwatch_object.CloudWatch_metric_data(constants.AvailiabilityMetric, constants.namespace, dimensions, availability)
    cloudwatch_object.CloudWatch_metric_data(constants.LatencyMetric, constants.namespace, dimensions, latency)
    return values




def getAvail():
    http = urllib3.PoolManager()
    response = http.request("GET", constants.url)
    if response.status == 200:
      return 1.0
    else:
      return  0.0


      

def getLatency():
    http = urllib3.PoolManager()
    start = datetime.datetime.now()
    response = http.request("GET", constants.url)
    end = datetime.datetime.now()
    delta = end - start
    latencySec = round(delta.microseconds * .000001, 6)
    return latencySec



