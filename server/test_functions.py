import pytest
import AppConfig

def test_env():
    env = AppConfig.Environment()
    assert env.getEnvironment() in [
        'localdev', 'localprod', 'clouddev', 'cloudprod', 'localTest', 'cloudTest'
    ]

