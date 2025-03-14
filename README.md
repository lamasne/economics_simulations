# Economics Simulations

## Documentation  
Refer to the `documentation` folder for detailed information.  

## A) Running the Code on Your Machine  

### 1) Directly on Local Machine  
- Create a virtual environment and install dependencies. For instance, in a Windows powershell (e.g. from within VScode):
  ```sh
  python3 -m venv venv
  source venv/Scripts/activate
  pip install -r meta/settings/requirements.txt
  ```
- Set `is_local_run = 1` in `meta/settings/meta_settings`.  
- Run an instance of **MongoDB** and match `host:port` with `meta_settings` variables.  
- Run an instance of **RabbitMQ** and match `host:port` with `meta_settings` variables.  
- Start the application:  
  ```sh
  python main.py
  ```

### 2) As a Single Docker Container  
- Set `is_local_run = 0` in `meta/settings/meta_settings`.  
- Run:  
  ```sh
  docker-compose up --build
  ```
  **If errors occur:**  
  ```sh
  docker-compose -f docker-compose.yaml up --build --remove-orphans --force-recreate
  ```

### 3) As Multiple Containers (to check)  
```sh
docker build app -d
docker run -it app_image
```

## B) Debugging Code  

### 1) Access Container Files  
```sh
docker exec -it <container_id> sh
```

### 2) Copy File from Container to Local Machine (while running)  
```sh
docker cp trunk-eco_sim-1:/home/econ_simul/multipage.pdf .
```

## C) Maintaining the Code  

### 1) Clean Requirements (Not Fully Functional)  
```sh
pip-extra-reqs main.py db_interface dynamics meta objects
```
