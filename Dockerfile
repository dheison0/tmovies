FROM python:3.11-alpine
RUN apk update && apk add poetry
RUN adduser -Dh /src tmovies
USER tmovies
COPY . /src
WORKDIR /src
RUN poetry install --no-root
CMD ["poetry", "run", "./start.py"]