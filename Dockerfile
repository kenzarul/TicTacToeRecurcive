FROM python:3.9-slim-buster

ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY . /app/
EXPOSE 8000
CMD ["python", "manage.py", "runserver"]