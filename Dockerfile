FROM ubuntu
WORKDIR /app
RUN apt-get update && apt-get install -y git python3 python3-pip
RUN cd /app && git clone https://github.com/uuso/mailing_service.git

ENV MAIL_USERNAME=PASTE-VALUE-HERE \
    MAIL_PASSWORD=PASTE-VALUE-HERE \
    MAIL_SERVER=PASTE-VALUE-HERE \
    MAIL_PORT=PASTE-VALUE-HERE \
    MAIL_SSL=True \
	MAIL_FROM=PASTE-VALUE-HERE \
	MAIL_TO=PASTE-VALUE-HERE \
	MAIL_ATTACHFOLDER="/app/share" \
	MAIL_DELAY=10

ENTRYPOINT ["python3"]
CMD ["/app/mailing_service/app.py"]