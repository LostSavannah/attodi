FROM python:3.12-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./src .
COPY ./LICENSE .
COPY ./README.md .
COPY ./pyproject.toml .

RUN python3 -m build
RUN pip install $(ls ./dist/*.whl | head -n 1)

COPY ./tests .

RUN python3 -m pytest

COPY ./project_updater.py .

RUN python3 ./project_updater.py "file=./pyproject.toml" "set-version-patch=2"

CMD [ "/bin/sh" ]