FROM python:3.10-alpine

WORKDIR /app
COPY monitor.py .

RUN chmod +x /app/monitor.py && \
    pip install --upgrade pip && \
    pip install proxmoxer requests

# Run the cron every minute
RUN echo '*  *  *  *  *    /usr/local/bin/python /app/monitor.py' >> /etc/crontabs/root

CMD ["python", "/app/monitor.py"]

#LABEL org.opencontainers.image.source=https://github.com/captmicr0/stale-NFS-handle-monitor
