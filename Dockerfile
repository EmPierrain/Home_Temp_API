FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
RUN apk --update add bash nvim
COPY ./src /app
COPY ./requirement.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
