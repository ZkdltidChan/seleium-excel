FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /code

VOLUME /code

CMD ["python", "main2.py"]