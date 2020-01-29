FROM python:3.7.6
RUN mkdir /app
COPY .  /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP=app.py
CMD python -m flask run --host=0.0.0.0
#CMD uwsgi --http 0.0.0.0:8080 -w app -p 2  # use 2 worker processes
