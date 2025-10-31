FROM python:3.11-slim

WORKDIR /workspace

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

COPY poetry.lock poetry.toml pyproject.toml poe_tasks.toml src/ .

RUN pip install --upgrade pip && pip install poetry==1.8.5 && poetry install --only main

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "poe", "run"]
