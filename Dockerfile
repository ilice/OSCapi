FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN python ./manage.py migrate --settings=osc.settings.dev.app_settings
CMD ["python", "./manage.py", "runserver", "--settings=osc.settings.dev.app_settings"]
