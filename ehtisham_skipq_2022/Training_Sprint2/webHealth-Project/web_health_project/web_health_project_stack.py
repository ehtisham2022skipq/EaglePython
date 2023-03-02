
from aws_cdk import (
    Duration,
    aws_events as events_,
    aws_iam as iam_,
    aws_lambda as lambda_,
    Stack,
    aws_events_targets as target_,
    RemovalPolicy,
    aws_cloudwatch as cw_,
    aws_sns as sns_,
    aws_sns_subscriptions as subscriptions_,
    aws_cloudwatch_actions as cw_actions,

)
from constructs import Construct
from resources import constants as constants


class WebHealthProjectStack(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)
    # creating lambda fn to deploy WHLambda.py
    lambda_role = self.create_lambda_role()
    fn=self.create_lambda("WHLambda", './resources', 'WHApp.lambda_handler', lambda_role)
    fn.apply_removal_policy(RemovalPolicy.DESTROY)
    # creating cronjob
      # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_events/Schedule.html  
        # defining schedule of the event
    schedule=events_.Schedule.rate(Duration.minutes(60))
            
        # defining target of the event 
    target=target_.LambdaFunction(handler=fn)
        
        # Defining rule to bind event and target
    rule = events_.Rule(self, "LambdaEventRule",
          description="rule to generate auto events fro lambda fn",
          schedule=schedule,
          targets=[target])
        # To destroy all the resources after infradtructure goes down
    rule.apply_removal_policy(RemovalPolicy.DESTROY)

    # creating SNS topics subscriptions
    topic=sns_.Topic(self, "WHNotification")
    topic.add_subscription(subscriptions_.EmailSubscription('ehtisham.hashmi.skipq@gmail.com'))

    dimensions={'url':constants.url}
    availability_metric=cw_.Metric(
      metric_name=constants.AvailiabilityMetric,
      namespace=constants.namespace,
      dimensions_map=dimensions
    )
    availability_alarm=cw_.Alarm(self, "Errors",
      metric=availability_metric,
      evaluation_periods=60,
      threshold=1,
      comparison_operator=cw_.ComparisonOperator.LESS_THAN_THRESHOLD                           
    )
    # linking alarm with subscription
    availability_alarm.add_alarm_action(cw_actions.SnsAction(topic))
    
    latency_metric=cw_.Metric(
      metric_name=constants.LatencyMetric,
      namespace=constants.namespace,
      dimensions_map=dimensions
    )

    latency_alarm=cw_.Alarm(self,"Error",
      metric=latency_metric,
      evaluation_periods=60,
      threshold=0.1,
      comparison_operator=cw_.ComparisonOperator.GREATER_THAN_THRESHOLD
    )
    # linking alarm with subscription
    latency_alarm.add_alarm_action(cw_actions.SnsAction(topic))




  def create_lambda(self, id, asset, handler, role):
    return lambda_.Function(self,
      id=id,
      handler=handler,
      role=role,
      code=lambda_.Code.from_asset(asset),
      runtime=lambda_.Runtime.PYTHON_3_9)

  def create_lambda_role(self):
    lambdaRole=iam_.Role(self, "Lambda_Role",
    assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
    managed_policies=[
      iam_.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess")
    ])
    return lambdaRole 


        

