#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis
#  All rights reserved.
#

from cloud_native_benchmarks import __version__


def test_version():
    assert __version__ is not None
