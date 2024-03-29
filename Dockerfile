# docker build --platform linux/amd64 -t nojson/clip-api:20240329.3 .

FROM python:3.8-slim-buster

RUN apt update && \
    apt install -y wget git git-lfs \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/models && cd /opt/models && git clone https://huggingface.co/openai/clip-vit-base-patch32

## Install Conda Apps
RUN mkdir -p /opt/conda && cd /opt/conda && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.12.0-Linux-x86_64.sh -O /opt/conda/miniconda.sh && \
    bash /opt/conda/miniconda.sh -b -p /opt/miniconda && \
    /opt/miniconda/bin/./conda install pytorch torchvision cpuonly -c pytorch && \
    rm -rf /opt/conda /opt/miniconda

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#### Use the previous cache to save build time
COPY requirements.txt.add requirements.txt
RUN pip3 install -r requirements.txt

COPY app.py .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# python3 -m flask run --host=0.0.0.0


