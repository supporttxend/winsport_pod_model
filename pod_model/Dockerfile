From nvidia/cuda:11.6.2-base-ubuntu20.04


ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda init bash && \
    . /root/.bashrc && \
    conda update conda && \
    conda activate base && \
    conda install pip

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/pod_model:${PATH}"

WORKDIR /opt/ml/pod_model
COPY . .

COPY requirements.txt .

RUN pip install -r requirements.txt

