import os

is_local_run = 0  # 1 if service is running directly on local machine, 0 if service is running from container

# IO folders
outputs_folder = os.path.normpath(
    "C:/Users/Lamas/workspace/PROJECTS/economics/simulation/outputs/"
)

# Communication between services - Rabbit MQ
RABBIT_MQ_HOST = "localhost" if is_local_run else "host.docker.internal"
PORT = 5673

# MongoDB connection settings
MONGO_DB_SETTINGS = {
    "host": "localhost" if is_local_run else "mongodb",
    "port": 27017,  # 27018 can usually be used if > 1 MongoDB instance
    "db_name": "econ_simulation",
    "db_backup": "econ_init_1",
}
