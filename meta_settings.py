import os

# IO folders
outputs_folder = os.path.normpath(
    "C:/Users/Lamas/workspace/PROJECTS/economics/simulation/outputs/"
)

# Communication between services - Rabbit MQ
RABBIT_MQ_HOST = "host.docker.internal"  # if service is running from container
# RABBIT_MQ_HOST = "localhost"  # if sercice is running directly on machine
PORT = 5673
