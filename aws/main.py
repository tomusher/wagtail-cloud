from typing import Any

from cdktf import TerraformStack
from constructs import Construct

from imports.aws import AwsProvider
from imports.random import RandomProvider

from .cache import Cache
from .config import StackConfig
from .database import Database
from .media import Media
from .network import Network
from .registry import ContainerRegistry
from .wagtail import WagtailApp

SCALE_MAP: dict[StackConfig.Scale, Any] = {
    StackConfig.Scale.TINY: {
        "app": {"cpu": "256", "memory": "512"},
        "db": {"instance_class": "db.t3.micro"},
        "cache": {"instance_class": "cache.t3.micro"},
    },
    StackConfig.Scale.SMALL: {
        "app": {"cpu": "512", "memory": "1024"},
        "db": {"instance_class": "db.t3.small"},
        "cache": {"instance_class": "cache.t3.small"},
    },
    StackConfig.Scale.BIG: {
        "app": {"cpu": "1024", "memory": "2048"},
        "db": {"instance_class": "db.t3.medium"},
        "cache": {"instance_class": "cache.t3.medium"},
    },
    StackConfig.Scale.HUGE: {
        "app": {"cpu": "2048", "memory": "4096"},
        "db": {"instance_class": "db.t3.large"},
        "cache": {"instance_class": "cache.t3.medium"},
    },
}


class AwsWagtailStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, *, config: StackConfig):
        super().__init__(scope, ns)
        scale = SCALE_MAP[config.scale]
        AwsProvider(self, "Aws", region=config.region)
        RandomProvider(self, "Random")
        network = Network(self, "Network", name=config.name, region=config.region)
        registry = ContainerRegistry(
            self,
            "ContainerRegistry",
            name=config.name,
            network=network,
            region=config.region,
        )
        db = Database(
            self, "Database", name=config.name, scale=scale["db"], network=network
        )
        cache = Cache(
            self, "Cache", name=config.name, scale=scale["cache"], network=network
        )
        media = Media(self, "Media", name=config.name, media_domain=config.media_domain)
        app = WagtailApp(
            self,
            "WagtailApp",
            name=config.name,
            scale=scale["app"],
            network=network,
            media=media,
            db=db,
            image=f"{registry.repo_path}:latest",
        )
