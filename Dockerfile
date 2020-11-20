FROM python:3.8.3

RUN mkdir baymax-backend && cd baymax-backend
WORKDIR /baymax-backend
ADD . /baymax-backend

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

# ENTRYPOINT [ "python" ]
CMD [ "python", "app.py" ]