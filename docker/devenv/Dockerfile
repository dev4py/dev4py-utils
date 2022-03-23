FROM python:alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache curl gcc musl-dev libressl-dev libffi-dev
RUN curl -sSL  https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"

ENTRYPOINT ["sh", "-c", "./project.py load_deps && $@", "-s"]
CMD sh
