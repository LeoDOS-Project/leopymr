FROM python:3.12-slim

RUN apt-get update && apt-get install -y screen
RUN apt-get install -y libgdal-dev gdal-bin python3-pip python3-gdal python3-dev build-essential
RUN pip3 install GDAL==`gdal-config --version`
RUN apt-get install -y libgl1 libglib2.0-0 libglu1-mesa-dev
WORKDIR /server
COPY requirements.txt.ml .
RUN pip3 install --no-cache-dir -r requirements.txt.ml
COPY . .
CMD ["./start_orb.sh"]

