FROM python:3.8.3

# RUN mkdir baymax-backend && cd baymax-backend
WORKDIR /baymax-backend
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

# ENTRYPOINT [ "python" ]
CMD [ "flask", "run" ]