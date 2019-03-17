FROM centos:7

RUN yum -y install python gcc python-devel MySQL-python python-setuptools libev-devel git

RUN easy_install pip

ADD . .

RUN pip install -r requirements.txt

ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 8000

ENV REDIS_HOST redis

WORKDIR ./
CMD python ./app/app.py