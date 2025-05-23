FROM python:3.12-bookworm
RUN mkdir /app
WORKDIR /app
COPY src/requirements.txt /app
RUN pip install -r requirements.txt
COPY src/ /app
CMD ["/usr/bin/env", "python3", "app.py"]