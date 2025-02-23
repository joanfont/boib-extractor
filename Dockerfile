FROM library/python:3.13-alpine
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:${PYTHONPATH}

WORKDIR /app

RUN pip3 --no-cache-dir install -U pip

ADD requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

ADD . .
ENTRYPOINT ["python3", "boib/cli.py"]