FROM python:3.11-bookworm
RUN mkdir /app
WORKDIR /app
COPY merger/src/requirements.txt /app
RUN pip install -r requirements.txt
COPY merger/src/ /app
CMD ["/usr/bin/env", "python3", "app.py"]
