FROM marun/dind_python:latest

WORKDIR /app

RUN apk add supervisor
RUN mv /etc/supervisord.conf /etc/supervisord.conf.org
COPY supervisord.conf /etc/supervisord.conf
RUN touch /var/log/aenode.log

ENTRYPOINT ["/usr/bin/supervisord"]
#ENTRYPOINT ["dockerd-entrypoint.sh"]
CMD []
