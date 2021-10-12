#!/usr/bin/env python
from cdktf import App

from aws.main import AwsWagtailStack, StackConfig

app = App()
AwsWagtailStack(
    app,
    "cdktf-wagtail-aws",
    config=StackConfig(
        name="wagtail-bakery",
        region="eu-west-1",
        scale=StackConfig.Scale.TINY,
        domain="bakery.usher.dev",
        media_domain="media-bakery.usher.dev",
    ),
)


app.synth()
