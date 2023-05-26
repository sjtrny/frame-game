FROM python:3.9-bullseye

WORKDIR /usr/src

COPY src ./

RUN apt-get update && apt-get install -y python3-opencv

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir assets/imgs
RUN chmod 777 assets/imgs

RUN mkdir assets/imgs_kps
RUN chmod 777 assets/imgs_kps

RUN python3 generate_data.py

CMD ["gunicorn"  , "-b", "0.0.0.0:80", "app:server"]
