#
FROM python:3.13-slim

#
WORKDIR /code

#
RUN pip install poetry

#
COPY . /code/

#
RUN poetry config virtualenvs.create false

#
RUN poetry install --no-root --no-interaction --no-ansi