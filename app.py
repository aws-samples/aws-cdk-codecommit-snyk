#!/usr/bin/env python3

from aws_cdk import core


from cdk_stack_deploy.cdk_snyk_stack import CdkSnykStack


app = core.App()
CdkSnykStack(app,'cdk-snyk-stack')
app.synth()
