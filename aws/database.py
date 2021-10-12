from constructs import Construct

from imports.aws import DbInstance
from imports.postgresql import Database as PostgresqlDatabase
from imports.postgresql import PostgresqlProvider
from imports.postgresql import Role as PostgresqlRole
from imports.random import Password

from .network import Network


class Database(Construct):
    def __init__(
        self, scope: Construct, ns: str, *, name: str, scale: dict, network: Network
    ):
        super().__init__(scope, ns)
        username = "postgresql"
        password = Password(self, "DbPassword", length=32, special=False)

        self.instance = DbInstance(
            self,
            "DbInstance",
            allocated_storage=10,
            max_allocated_storage=1000,
            engine="postgres",
            engine_version="13.3",
            auto_minor_version_upgrade=True,
            instance_class=scale["instance_class"],
            vpc_security_group_ids=[network.db_security_group.id],
            db_subnet_group_name=network.vpc.database_subnet_group_name_output,
            iam_database_authentication_enabled=True,
            apply_immediately=True,
            username=username,
            password=password.result,
            skip_final_snapshot=True,
            port=5432,
            publicly_accessible=True,
        )

        PostgresqlProvider(
            self,
            "Postgresql",
            scheme="awspostgres",
            host=self.instance.address,
            port=5432,
            username=username,
            password=password.result,
            superuser=False,
            expected_version="13.3",
        )

        self.role = PostgresqlRole(
            self,
            "AppRole",
            name=name,
            login=True,
            roles=["rds_iam"],
        )
        self.db = PostgresqlDatabase(
            self, "AppDatabase", name=name, owner=self.role.name
        )

    @property
    def app_connection_string(self):
        return f"postgresql://{self.role.name}@{self.instance.address}:{self.instance.port}/{self.db.name}"
