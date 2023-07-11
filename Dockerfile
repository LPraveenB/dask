FROM docker.io/daskdev/dask:latest-py3.10

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get update && \
    apt-get install -y software-properties-common \
                       git \
                       curl


# Add the Google Cloud public key and package repository
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update the package list and install gcloud
RUN apt-get update && apt-get install -y google-cloud-sdk

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
RUN pip3 install -r requirements.txt
#RUN bash git_clone.sh

COPY environment.yml /app
RUN mkdir /app/.config
RUN mkdir /app/.config/dask/
RUN touch /app/.config/dask/cloudprovider.yamlz
COPY cloudprovider.yaml /app/.config/dask/cloudprovider.yaml
COPY gcp_dask.py /app
COPY dask.json /app

ENTRYPOINT ["python", "gcp_dask.py"]