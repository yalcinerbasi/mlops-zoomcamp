FROM python:3.9-slim-buster

RUN pip install -U pip

WORKDIR /app

COPY [ "requirements.txt", "./" ]

RUN pip install -r requirements.txt

COPY [ "app.py", "model.pkl", "dv.pkl", "./" ]

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "app:app" ]
