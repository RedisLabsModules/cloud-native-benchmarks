[![codecov](https://codecov.io/gh/RedisLabsModules/cloud-native-benchmarks/branch/main/graph/badge.svg?token=IE174TJJ6A)](https://codecov.io/gh/RedisLabsModules/cloud-native-benchmarks)
[![CI tests](https://github.com/RedisLabsModules/cloud-native-benchmarks/actions/workflows/tox.yml/badge.svg)](https://github.com/RedisLabsModules/cloud-native-benchmarks/actions/workflows/tox.yml)
[![PyPI version](https://badge.fury.io/py/cloud-native-benchmarks.svg)](https://badge.fury.io/py/cloud-native-benchmarks)
-----

# cloud-native-benchmarks

This repo contains code for benchmarking several DBMS cloud native providers, 
broken down by database model, including Redis Cloud, Amazon MemoryDB, 
Amazon DocumentDB, Amazon ElasticCache, Elastic Cloud, and MongoDB Atlas.

Current databases supported, by database model:

## Key-Value

+ Redis Cloud [(supplemental docs)](docs/keyvalue/redis-cloud.md)
+ Amazon ElasticCache [(supplemental docs)](docs/keyvalue/amazon-elasticcache.md)
+ Amazon MemoryDB [(supplemental docs)](docs/keyvalue/amazon-memorydb.md)

## Document databases

+ Redis Cloud with RedisJSON* [(supplemental docs)](docs/document/redis-cloud.md)
+ MongoDB Atlas [(supplemental docs)](docs/document/mongodb-atlas.md)
+ Elastic Cloud [(supplemental docs)](docs/document/elastic-cloud.md)
+ Amazon DocumentDB [(supplemental docs)](docs/document/amazon-documentdb.md)

# Installation

To have access to the latest SPEC and Tooling implementation you only need to install one python package.

Installation is done using pip, the package installer for Python, in the following manner:

```bash
python3 -m pip install cloud-native-benchmarks --ignore-installed PyYAML
```

