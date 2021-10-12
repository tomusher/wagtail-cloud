from constructs import Construct

from imports.aws import S3Bucket


class Media(Construct):
    def __init__(self, scope: Construct, ns: str, *, name: str, media_domain: str):
        super().__init__(scope, ns)

        self.bucket = S3Bucket(
            self,
            "S3Bucket",
            bucket=media_domain,
            acl="public-read",
        )
