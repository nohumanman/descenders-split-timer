# Official python runtime
FROM python:3.12

# set working directory
WORKDIR /app
# copy application code
COPY ../common/requirements.txt .

RUN pip install --upgrade pip

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ../common/ ./common/

# copy application code
COPY ./web-api .

# expose webserver port
EXPOSE 8082

RUN ls -l /app/requirements.txt

# run application
CMD ["hypercorn", "main:webserver_app", "-b", "0.0.0.0:8082"]