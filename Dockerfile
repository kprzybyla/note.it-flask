FROM python:3.9

COPY . /app

RUN pip install \
        meinheld \
        gunicorn \
        /app/dist/*.whl \
    && chmod +x /app/run.sh

CMD ["/app/run.sh"]
