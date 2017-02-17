FROM python:2.7
CMD ["python", "./manage.py", "runserver", "--settings=osc.settings.cpd.app_settings"]
