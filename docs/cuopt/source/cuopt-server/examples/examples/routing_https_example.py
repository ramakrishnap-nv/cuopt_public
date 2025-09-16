from cuopt_sh_client import CuOptServiceSelfHostClient

data = {"cost_matrix_data": {"data": {"0": [[0,1],[1,0]]}},
        "task_data": {"task_locations": [0,1]},
        "fleet_data": {"vehicle_locations": [[0,0],[0,0]]}}

# If cuOpt is not running on localhost:5000, edit ip and port parameters
cuopt_service_client = CuOptServiceSelfHostClient(
    ip="localhost",
    port=5000,
    use_https=True
)
