# MongoDB connection settings
connection_settings = {
    # "host": "localhost", # if service is running directly on local machine
    "host": "mongodb",  # if service is running from container
    "port": 27017,  # 27018 can usually be used if > 1 MongoDB instance
    "db_name": "econ_simulation",
    "db_backup": "econ_init_1",
}
