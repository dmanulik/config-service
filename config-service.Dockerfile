ARG BASE_IMAGE_TAG
FROM python:${BASE_IMAGE_TAG}

WORKDIR /flaskr

COPY ./flaskr/ /flaskr

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["service.py"]
