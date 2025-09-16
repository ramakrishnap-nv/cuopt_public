from cuopt_sh_client import CuOptServiceSelfHostClient
import json
import time

data = {"cost_matrix_data": {"data": {"0": [[0,1],[1,0]]}},
        "task_data": {"task_locations": [0,1]},
        "fleet_data": {"vehicle_locations": [[0,0],[0,0]]}}

# If cuOpt is not running on localhost:5000, edit ip and port parameters
cuopt_service_client = CuOptServiceSelfHostClient(
    ip="localhost",
    port=5000,
    timeout_exception=False
)

# Get initial solution
# Set delete_solution to false so it can be used in next request
initial_solution = cuopt_service_client.get_optimized_routes(
    data, delete_solution=False
)


# Upload a solution returned/saved from previous request as initial solution
initial_solution_3 = cuopt_service_client.upload_solution(initial_solution)

# Use previous solution saved in server as initial solution to this request.
# That solution is referenced with previous request id.
solution = cuopt_service_client.get_optimized_routes(
    data,
    initial_ids=[
        initial_solution["reqId"],
        initial_solution_3["reqId"]
    ]
)

print(json.dumps(solution, indent=4))

# Delete saved solution if not required to save space
cuopt_service_client.delete(initial_solution["reqId"])
cuopt_service_client.delete(initial_solution_3["reqId"])

# Another option is to add a solution that was generated
# to data model option as follows
initial_solution_2 = [
    {
        "0": {
            "task_id": ["Depot", "0", "1", "Depot"],
            "type": ["Depot", "Delivery", "Delivery", "Depot"]
        }
    }
]

data["initial_solution"] = initial_solution_2
solution = cuopt_service_client.get_optimized_routes(data)

print(json.dumps(solution, indent=4))
