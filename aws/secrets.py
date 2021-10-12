from constructs import Construct


class ContainerRegistry(Construct):
    def __init__(self, scope: Construct, ns: str, *, name: str):
        super().__init__(scope, ns)
