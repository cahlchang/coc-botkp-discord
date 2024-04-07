FROM public.ecr.aws/lambda/python:3.9
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY xml/ ./xml/
COPY .env ./
COPY handler.py ./
COPY yig/ ./yig/
CMD ["handler.run"]
