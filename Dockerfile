FROM ubuntu:20.04 

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./resident.py .
COPY ./style.css .
COPY ./api.py .
COPY ./api_wrapper.py .
EXPOSE 49190
ENV SERVER=
ENV RESIDENT_CLIENT=mosip-resident-client
ENV RESIDENT_SECRET=
WORKDIR ./
CMD python3 resident.py
