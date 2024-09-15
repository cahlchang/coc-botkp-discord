FROM public.ecr.aws/lambda/python:3.12 as builder

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .
COPY yig/ ./yig/

FROM public.ecr.aws/lambda/python:3.12

COPY --from=builder /var/task /var/task
COPY --from=builder /opt/python /opt/python

COPY xml/ ./xml/
COPY font/ ./font/
COPY .env .

ENV PYTHONPATH=/var/task

CMD ["handler.handle"]
