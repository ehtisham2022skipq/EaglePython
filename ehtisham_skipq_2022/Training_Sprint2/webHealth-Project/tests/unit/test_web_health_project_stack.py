import aws_cdk as core
import aws_cdk.assertions as assertions

from web_health_project.web_health_project_stack import WebHealthProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in web_health_project/web_health_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WebHealthProjectStack(app, "web-health-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
