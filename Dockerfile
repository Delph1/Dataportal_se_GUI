FROM python:3.11

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

# If running behind a proxy like Nginx or Traefik add --proxy-headers
CMD ["fastapi", "run", "/code/app/main.py", "--port", "80", "--proxy-headers"]