FROM python:slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography

COPY auth ./auth
COPY errors ./errors
COPY main ./main
COPY models ./models
COPY static ./static
COPY templates ./templates
COPY migrations ./migrations
COPY app.py default_config.py extensions.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP='app:create_app()'

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
