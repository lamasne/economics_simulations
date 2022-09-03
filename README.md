# economics_simulations
For documentation cf. folder documentation

To run the code on your machine: 
1) Directly on local machine:
- create a venv with requirements from documentations/requirements.txt (obtained via pip3 freeze)
-
2) As a single container:
docker-compose up --build --remove-orphans --force-recreate

3) as various containers (to check):
docker build app -d
docker run -it app_image

Debugg code:
1) acces container files:
    docker exec -it container_id sh
2) copy file from container to local machine (only while container is running)
    docker cp trunk-eco_sim-1:/home/econ_simul/multipage.pdf .

Mantain the code:
1) Clean requirements: 
- pip-extra-reqs main.py db_interface dynamics meta objects (does not seem to work)