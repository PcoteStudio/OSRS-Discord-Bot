# ---- Compiler Image ----
FROM python:3.11-alpine AS build
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

# ---- Runtime Image ----
FROM python:3.11-alpine
WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/ .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "main.py"]