from cuopt_sh_client import CuOptServiceSelfHostClient

# This is an UUID that is returned by the solver while the solver is trying to find solution so users can come back and check the status or query for results.
job_uuid = "<UUID_THAT_WE_GOT>"

# If cuOpt is not running on localhost:5000, edit ip and port parameters
cuopt_service_client = CuOptServiceSelfHostClient(
    ip="localhost",
    port=5000
)

# Delete the job if it is still queued or running
response = cuopt_service_client.delete(job_uuid, running=True, queued=True, cached=False)

print(response)
