from constructs import Construct

from imports.aws import ElasticacheCluster

from .network import Network


class Cache(Construct):
    def __init__(
        self, scope: Construct, ns: str, *, name: str, scale: dict, network: Network
    ):
        super().__init__(scope, ns)
        self.instance = ElasticacheCluster(
            self,
            "ElasticacheCluster",
            cluster_id=f"{name}-elasticache-cluster",
            engine="redis",
            node_type=scale["instance_class"],
            num_cache_nodes=1,
            security_group_ids=[network.cache_security_group.id],
            subnet_group_name=network.vpc.elasticache_subnet_group_name_output,
        )
