FROM tiangolo/uwsgi-nginx-flask:python3.12
RUN apt-get update \
	&& apt-get install -y --no-install-recommends bash \
	&& rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/conf.d/nginx.conf
COPY ./src /app
COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
	&& pip install -r /app/requirements.txt
ENV TZ="Europe/Paris"
