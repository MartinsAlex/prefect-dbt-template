import yaml
from prefect.client.orchestration import PrefectClient as Client
from prefect.deployments import Deployment
import importlib.util
from prefect.flows import Flow
from pathlib import Path

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

async def main():
    client = Client(api="http://127.0.0.1:4200/api", httpx_settings=httpx_settings)

    # Iterate through flows in the YAML
    for flow_info in data['flows']:
        file_path = Path(flow_info['path'])
        spec = importlib.util.spec_from_file_location(flow_info['name'], file_path)
        flow_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flow_module)

        # Fetch the flow object or function from the module
        flow_obj_or_func = getattr(flow_module, flow_info['entrypoint'])

        # Register Flow
        if isinstance(flow_obj_or_func, Flow):
            # If it's a Flow object, register it directly
            flow_to_register = flow_obj_or_func
        else:
            # If it's a function, create a Flow that calls the function
            flow_to_register = Flow(flow_obj_or_func)

        # Register Flow
        try:
            created_flow_uuid = await client.create_flow(flow_to_register)
            
            created_flow = await client.read_flow(created_flow_uuid)
            
            #print(created_flow)
            
            deployment = await Deployment.build_from_flow(
                flow=flow_to_register,
                name='hello world'
            )

            deployment.apply()
            
            # If scheduling info is provided, create a schedule (consider using Prefect Cloud Scheduler)
            if 'schedule' in flow_info:
                # Your scheduling code here
                pass

        except Exception as e:
            print(f"Failed to register {flow_info['name']} due to {str(e)}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
