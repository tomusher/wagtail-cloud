from constructs import Construct

from imports.aws import SecurityGroup
from imports.terraform_aws_modules.vpc.aws import TerraformAwsModulesVpcAws


class Network(Construct):
    def __init__(self, scope: Construct, ns: str, *, name: str, region: str):
        super().__init__(scope, ns)
        self.vpc = TerraformAwsModulesVpcAws(
            self,
            "Vpc",
            name=f"{name}-vpc",
            cidr="10.0.0.0/16",
            azs=[f"{region}a", f"{region}b", f"{region}c"],
            public_subnets=["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"],
            database_subnets=["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"],
            elasticache_subnets=["10.0.31.0/24", "10.0.32.0/24", "10.0.33.0/24"],
            create_database_subnet_group=True,
            create_database_subnet_route_table=True,
            create_database_internet_gateway_route=True,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            enable_nat_gateway=False,
            enable_vpn_gateway=False,
        )

        self.app_security_group = SecurityGroup(
            self,
            "AppSecurityGroup",
            vpc_id=self.vpc.vpc_id_output,
            ingress=[
                {
                    "fromPort": 80,
                    "toPort": 80,
                    "protocol": "TCP",
                    "cidrBlocks": ["0.0.0.0/0"],
                    "ipv6CidrBlocks": ["::/0"],
                }
            ],
            egress=[
                {
                    "fromPort": 0,
                    "toPort": 0,
                    "protocol": "-1",
                    "cidrBlocks": ["0.0.0.0/0"],
                    "ipv6CidrBlocks": ["::/0"],
                }
            ],
        )

        self.db_security_group = SecurityGroup(
            self,
            "DbSecurityGroup",
            vpc_id=self.vpc.vpc_id_output,
            ingress=[
                {
                    "fromPort": 5432,
                    "toPort": 5432,
                    "protocol": "TCP",
                    "securityGroups": [self.app_security_group.id],
                },
                {
                    "fromPort": 5432,
                    "toPort": 5432,
                    "protocol": "TCP",
                    "cidrBlocks": ["0.0.0.0/0"],
                    "ipv6CidrBlocks": ["::/0"],
                },
            ],
        )

        self.cache_security_group = SecurityGroup(
            self,
            "CacheSecurityGroup",
            vpc_id=self.vpc.vpc_id_output,
            ingress=[
                {
                    "fromPort": 6379,
                    "toPort": 6379,
                    "protocol": "TCP",
                    "securityGroups": [self.app_security_group.id],
                }
            ],
        )

    @property
    def vpc_id(self):
        return self.vpc.vpc_id_output
