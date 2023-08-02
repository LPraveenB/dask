ARG PYTHON_VERSION="3.9"
FROM python:${PYTHON_VERSION}


RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && \
    pip3 install setuptools && \
    rm get-pip.py
RUN python3 -m pip install --upgrade pip


ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    mkdir /root/.conda && \
    bash Miniconda3-latest-Linux-x86_64.sh -b && \
    rm -f Miniconda3-latest-Linux-x86_64.sh && \
    echo "Running $(conda --version)" && \
    conda init bash && \
    . /root/.bashrc && \
    conda update conda

#ENV CONDA_HOME=/opt/miniconda3
#ENV PYSPARK_PYTHON=${CONDA_HOME}/bin/python
#ENV PATH=${CONDA_HOME}/bin:${PATH}
#COPY Miniconda3-py310_23.3.1-0-Linux-x86_64.sh .
#RUN bash Miniconda3-py310_23.3.1-0-Linux-x86_64.sh -b -p /opt/miniconda3 \
#  && ${CONDA_HOME}/bin/conda config --system --set always_yes True \
#  && ${CONDA_HOME}/bin/conda config --system --set auto_update_conda False \
#  && ${CONDA_HOME}/bin/conda config --system --prepend channels conda-forge \
#  && ${CONDA_HOME}/bin/conda config --system --set channel_priority strict


WORKDIR /app

COPY requirements.txt /app
#COPY git_clone.sh /app
RUN pip install google-api-python-client


RUN rm -rf /train

RUN mkdir -p /train
COPY component/training/gcr_auth_key.json /train
ENV GOOGLE_APPLICATION_CREDENTIALS=/train/gcr_auth_key.json
COPY component/training/run_notebook_component.py /train
COPY component/training/generic_utils.py /train
COPY component/training/entrypoint.sh /train
COPY dask_cluster.py /train
COPY component/training/dask.json /train
ARG GCP_SA_KEY
ENV GOOGLE_APPLICATION_CREDENTIALS=/train/gcp_sa_key.json
RUN echo "$GCP_SA_KEY" > /train/gcp_sa_key.json

WORKDIR /train

ENTRYPOINT ["bash", "entrypoint.sh"]
