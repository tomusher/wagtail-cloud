import json

from constructs import Construct

from imports.aws import (
    DataAwsIamPolicyDocument,
    EcsCluster,
    EcsService,
    EcsTaskDefinition,
    IamRole,
)
from imports.random import Password

from .database import Database
from .media import Media
from .network import Network


class WagtailApp(Construct):
    def __init__(
        self,
        scope: Construct,
        ns: str,
        *,
        name: str,
        scale: dict,
        image: str,
        network: Network,
        media: Media,
        db: Database,
    ):
        super().__init__(scope, ns)
        secret_key = Password(self, "SecretKey", length=50, special=True)

        assume_role_policy_document = DataAwsIamPolicyDocument(
            self,
            "AssumeRolePolicyDocument",
            version="2012-10-17",
            statement=[
                {
                    "effect": "Allow",
                    "actions": ["sts:AssumeRole"],
                    "sid": "",
                    "principals": [
                        {"identifiers": ["ecs-tasks.amazonaws.com"], "type": "Service"}
                    ],
                }
            ],
        )

        registry_auth_policy_document = DataAwsIamPolicyDocument(
            self,
            "RegistryAuthPolicyDocument",
            version="2012-10-17",
            statement=[
                # {
                #     "effect": "Allow",
                #     "actions": ["ssm:GetParameters",],
                #     "resources": [],
                # },
                {
                    "effect": "Allow",
                    "actions": ["s3:PutObject", "s3:GetObject"],
                    "resources": [media.bucket.arn],
                },
                {
                    "effect": "Allow",
                    "actions": ["rds-db:connect"],
                    "resources": [
                        f"{db.instance.arn}/postgresql",
                        f"{db.instance.arn}/{name}",
                    ],
                },
            ],
        )

        task_execution_role = IamRole(
            self,
            "EcsTaskExecutionRole",
            assume_role_policy=assume_role_policy_document.json,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
            ],
            inline_policy=[
                {
                    "name": "access-registry-s3-db",
                    "policy": registry_auth_policy_document.json,
                }
            ],
        )

        cluster = EcsCluster(self, "EcsCluster", name=f"{name}-ecs-cluster")
        task_definition = EcsTaskDefinition(
            self,
            "EcsTaskDefinition",
            family="web",
            requires_compatibilities=["FARGATE"],
            cpu=scale["cpu"],
            memory=scale["memory"],
            network_mode="awsvpc",
            execution_role_arn=task_execution_role.arn,
            container_definitions=json.dumps(
                [
                    {
                        "name": "web",
                        "image": "foo",
                        "portMappings": [{"containerPort": 80, "hostPort": 80}],
                        "environment": [
                            {
                                "name": "DATABASE_URL",
                                "value": db.app_connection_string,
                            },
                            {"name": "SECRET_KEY", "value": secret_key.result},
                        ],
                    }
                ]
            ),
        )
        service = EcsService(
            self,
            "EcsService",
            name=f"{name}-ecs-service",
            cluster=cluster.id,
            launch_type="FARGATE",
            task_definition=task_definition.arn,
            network_configuration=[
                {
                    "subnets": [],
                    "security_groups": [network.app_security_group.id],
                    "assign_public_ip": True,
                }
            ],
        )
        service.add_override(
            "network_configuration.0.subnets", network.vpc.public_subnets_output
        )
