from constructs import Construct

from imports.aws import DataAwsCallerIdentity, EcrRepository

from .network import Network


class ContainerRegistry(Construct):
    def __init__(
        self, scope: Construct, ns: str, *, name: str, network: Network, region: str
    ):
        super().__init__(scope, ns)

        self.caller_identity = DataAwsCallerIdentity(self, "CallerIdentity")
        self.region = region

        self.repository = EcrRepository(
            self,
            "EcrRepository",
            name=f"{name}-ecr-repository",
        )

    @property
    def repo_path(self):
        return f"{self.caller_identity.account_id}.dkr.ecs.{self.region}.amazonaws.com/{self.repository.name}"
