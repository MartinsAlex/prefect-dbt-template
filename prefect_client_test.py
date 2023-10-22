import yaml
from prefect.client.orchestration import PrefectClient as Client
from prefect.deployments import Deployment
from prefect.flows import Flow
from pathlib import Path
import asyncio

# Load YAML
with open("./flows/deployments.yml", 'r') as stream:
    data = yaml.safe_load(stream)

headers = {
    "Custom-Header-1": "value1",
    "Custom-Header-2": "value2",
    "username": "value2",
    "password": "password"
    # ... other headers ...
}

# Additional httpx settings
httpx_settings = {"headers": headers}

async def get_flows():
    client = Client(api="http://127.0.0.1:4200/api", httpx_settings=httpx_settings)
    r = await client.read_flows(limit=5)
    return r

r = asyncio.run(get_flows())

for flow in r:
    print(flow)

if __name__ == "__main__":
    asyncio.run(get_flows())
