# Official python runtime
FROM python:3.12

# set working directory
WORKDIR /app

# copy application code
COPY ../common/requirements.txt .

COPY ../common/ ./common/

RUN pip install --upgrade pip

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY ./websocket-api .

# expose websocket port
EXPOSE 65432

# run application
CMD ["python3", "-u", "main.py"]
