FROM marun/dind_python:latest

WORKDIR /app

RUN apk add supervisor
RUN mv /etc/supervisord.conf /etc/supervisord.conf.org
COPY supervisord.conf /etc/supervisord.conf
RUN touch /var/log/aenode.log

RUN apk add git
#RUN pip install git+https://github.com/maru-n/AsyncALifeEngine.git

ENTRYPOINT ["/usr/bin/supervisord"]
#ENTRYPOINT ["dockerd-entrypoint.sh"]
CMD []
