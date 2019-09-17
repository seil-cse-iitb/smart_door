FROM tiangolo/uwsgi-nginx-flask:python3.5
# FROM frolvlad/alpine-python3

# alpine-python3 from https://hub.docker.com/r/frolvlad/alpine-python3/dockerfile
# RUN apk update
# RUN apk add make automake gcc g++ subversion python3-dev
# RUN echo "**** install Python3 ****" && \
#     apk add --no-cache python3 && \
#     if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
#     \
#     echo "**** install pip for python3 ****" && \
#     python3 -m ensurepip && \
#     rm -r /usr/lib/python*/ensurepip && \
#     pip3 install --no-cache --upgrade pip setuptools wheel && \
#     if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi


RUN mkdir -p /home/smart_door/flask_server/
WORKDIR /home/smart_door/flask_server/
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN python3 migrate.py

ENTRYPOINT bash start_flask_server.sh

