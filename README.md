# economics_simulations
For documentation cf. folder documentation

A) run the code on your machine: 
    1) Directly on local machine:
    - create a venv with requirements from requirements.txt (obtained via pip3 freeze > requirements.txt)
    - run an instance of MongoDB and match host:port with meta_settings relevant vars
    - run an instance of RabbitMQ and match host:port with meta_settings relevant vars
    - run python main

    2) As a single container:
        docker-compose up --build
    if get errors:
        docker-compose -f docker-compose.yaml up --build --remove-orphans --force-recreate

    3) as various containers (to check):
        docker build app -d
        docker run -it app_image

B) Debugg code:
    1) acces container files:
        docker exec -it container_id sh
    2) copy file from container to local machine (only while container is running)
        docker cp trunk-eco_sim-1:/home/econ_simul/multipage.pdf .

C) Mantain the code:
    1) Clean requirements: 
        (does not seem to work)
        pip-extra-reqs main.py db_interface dynamics meta objects