FROM python:3.9
RUN mkdir /Scout
WORKDIR /Scout
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY . /Scout/
CMD [ "python", "main.py"]
