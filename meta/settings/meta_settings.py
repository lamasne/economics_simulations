import os

# IO folders
outputs_folder = os.path.normpath(
    "C:/Users/Lamas/workspace/PROJECTS/economics/simulation/outputs/"
)

# Communication between services - Rabbit MQ
RABBIT_MQ_HOST = "localhost"  # if sercice is running directly on machine
# RABBIT_MQ_HOST = "host.docker.internal"  # if service is running from container
PORT = 5673

# MongoDB connection settings
MONGO_DB_SETTINGS = {
    "host": "localhost",  # if service is running directly on local machine
    # "host": "mongodb",  # if service is running from container
    "port": 27017,  # 27018 can usually be used if > 1 MongoDB instance
    "db_name": "econ_simulation",
    "db_backup": "econ_init_1",
}
