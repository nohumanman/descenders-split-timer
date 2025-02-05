# Official python runtime
FROM python:3.12

# set working directory
WORKDIR /app

# need requirements
COPY requirements.txt .

RUN pip install --upgrade pip

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# expose websocket port
EXPOSE 65432

# expose webserver port
EXPOSE 8082

# run application
CMD ["python", "main.py"]