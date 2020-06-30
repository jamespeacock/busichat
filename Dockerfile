FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

# We copy just the requirements.txt first to leverage Docker cache

RUN mkdir -p /app
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

ENV  LC_ALL C.UTF-8
ENV  LANG C.UTF-8

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv install --deploy --system

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
