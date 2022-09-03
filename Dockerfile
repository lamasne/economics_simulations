FROM python:3

WORKDIR /home/econ_simul

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
