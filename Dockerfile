FROM python:3.8

ARG PYTHON_ENV=production
ENV PYTHON_ENV=${PYTHON_ENV}

ARG DB_HOST
ENV DB_HOST=$DB_HOST

ARG DB_PORT
ENV DB_PORT=$DB_PORT

ARG DB_NAME
ENV DB_NAME=$DB_NAME

ARG DB_USER
ENV DB_USER=$DB_USER

ARG DB_PASSWORD
ENV DB_PASSWORD=DB_PASSWORD

WORKDIR /app



COPY requirements.txt .
COPY core/ ./core
COPY api ./api
COPY manage.py .
COPY init_db.py .
RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 8000/TCP

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
