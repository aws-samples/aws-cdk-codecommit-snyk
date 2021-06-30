from aws_cdk import (
    core,
    aws_events as events,
    aws_codepipeline as pipeline,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_events_targets as events_targets,
    aws_codepipeline_actions as cpactions,
    aws_ssm as ssm,
    aws_iam as iam
)
import os

class CdkSnykConstructStack(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str,
                    props,
                    **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # For this construct to work, at least the following three parameters should be passed
        # 1. Name of the CodeCommit repository to be scanned
        # 2. Snyk Org ID
        # 3. Snyk Auth token
        codecommit_reponame = props['repoarn']
        account = os.environ['CDK_DEFAULT_ACCOUNT']
        region = os.environ['CDK_DEFAULT_REGION']

        snyk_build_project= codebuild.PipelineProject(
            self, 'snykBuild',
            build_spec= codebuild.BuildSpec.from_object(
            {
                "version": '0.2',
                "env": {
                    "parameter-store":{
                        "SNYK_TOKEN": props['snyk-auth-code'],
                        "SNYK_ORG": props['snyk-org-id']
                    }
                },
                "phases":{
                    "install":{
                        "commands":[
                            "echo 'installing Snyk'",
                            "npm install -g snyk"
                        ]
                    },
                    "pre_build":{
                        "commands":[
                            "echo 'authorizing Snyk'",
                            "snyk config set api=$SNYK_TOKEN"
                        ]
                    },
                    "build":{
                        "commands":[
                            "echo 'starting scan'",
                            "pip install -r requirements.txt",
                            "snyk monitor --file=requirements.txt --org=$SNYK_ORG --project-name={} --package-manager=pip".format(codecommit_reponame)
                        ]
                    },
                    "post_build":{
                        "commands":[
                            "echo ***build complete****"
                        ]
                    }
                }
            }
            ),
            environment = codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                compute_type=codebuild.ComputeType.LARGE
            )
        )
        snyk_build_project.add_to_role_policy(iam.PolicyStatement(
            actions=['ssm:GetParameters'],
            effect = iam.Effect.ALLOW,
            resources= [
                        'arn:aws:ssm:{}:{}:parameter/{}'.format(region,account,props['snyk-auth-code']),
                        'arn:aws:ssm:{}:{}:parameter/{}'.format(region,account,props['snyk-org-id'])
                        ]
        ))
        source_artifact = pipeline.Artifact()
        snyk_pipeline = pipeline.Pipeline(self,'snyk_pipeline',
                stages =[
                    pipeline.StageProps(
                        stage_name = 'sourcestage',
                        actions=[
                            cpactions.CodeCommitSourceAction(
                                action_name='codecommit',
                                output=source_artifact,
                                branch= props['repo-branch'],
                                repository=codecommit.Repository.from_repository_name(self,'cc_repository',codecommit_reponame)
                            )
                        ]
                    ),
                    pipeline.StageProps(
                        stage_name='build',
                        actions= [
                            cpactions.CodeBuildAction(
                                action_name='SnykStage',
                                input=source_artifact,
                                project=snyk_build_project,
                                check_secrets_in_plain_text_env_variables = True,
                                run_order = 2
                            )
                        ]
                    )
                ]
                )