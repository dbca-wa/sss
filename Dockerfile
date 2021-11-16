FROM ubuntu:18.04 as builder_base_gokart
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Perth
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev \
  python python-setuptools python-dev python-pip tzdata python-numpy g++ software-properties-common \
  tesseract-ocr tesseract-ocr-eng libtesseract-dev lftp unzip zip curl \
  && pip install --upgrade pip
# Everything below is required to install GDAL.
RUN add-apt-repository ppa:ubuntugis/ppa \
  && apt-get update -y \
  && apt-get install -y gdal-bin libgdal-dev \
  && rm -rf /var/lib/apt/lists/*
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Lines below are required to install pdktk in Ubuntu 18.04.
# Reference: https://askubuntu.com/a/1046476/4364
COPY external_libs/*.deb /tmp/
RUN apt-get update \
  && cd /tmp \
  && apt-get install -y ./libgcj17_6.4.0-8ubuntu1_amd64.deb ./libgcj-common_6.4-3ubuntu1_all.deb ./pdftk_2.02-4build1_amd64.deb ./pdftk-dbg_2.02-4build1_amd64.deb \
  && rm /tmp/*.deb \
  && rm -rf /var/lib/apt/lists/*


# Install Python libs from requirements.txt.
FROM builder_base_gokart as python_libs_gokart
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_gokart
COPY dist/release ./dist/release
COPY ftp_sync ./ftp_sync
COPY gokart ./gokart
COPY uwsgi.ini.prod ./uwsgi.ini
COPY tessdata/bom.traineddata /usr/local/share/tessdata/
USER www-data
EXPOSE 8080
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
