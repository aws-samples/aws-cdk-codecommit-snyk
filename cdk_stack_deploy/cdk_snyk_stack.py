from aws_cdk import (core)
from cdk_snyk_construct.cdk_snyk_construct_stack import CdkSnykConstructStack


class CdkSnykStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo_arn = core.CfnParameter(
            self,
            "RepoName",
            type="String",
            default='tjf721',
            description="Name of the CodeCommit repository to be scanned by Snyk"
        )

        repo_branch = core.CfnParameter(
            self,
            "RepoBranch",
            type="String",
            default='main',
            description="Name of the CodeCommit repository to be scanned by Snyk"
        )

        snyk_org_id = core.CfnParameter(
            self,
            "SnykOrgId",
            type="String",
            default='snykPSOrg',
            description="Name of SSM parameter which stores the Snyk Org ID"
        )

        snyk_auth = core.CfnParameter(
            self,
            "SnykAuthToken",
            type="String",
            default='snykauth2',
            description="Name of SSM parameter which stores the Snyk Auth token"
        )     

        props = {}
        props['repoarn']= repo_arn.value_as_string
        props['snyk-org-id']=snyk_org_id.value_as_string
        props['snyk-auth-code']=snyk_auth.value_as_string
        props['repo-branch'] = repo_branch.value_as_string

        CdkSnykConstructStack(self,'cdk-snyk-construct',props)