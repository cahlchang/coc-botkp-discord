#FROM public.ecr.aws/lambda/python:3.12 as builder
FROM public.ecr.aws/lambda/python:3.12-arm64 as builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /var/task/

#FROM public.ecr.aws/lambda/python:3.12
FROM public.ecr.aws/lambda/python:3.12-arm64
COPY --from=builder /var/task /var/task

COPY handler.py .
COPY yig/ ./yig/
COPY xml/ ./xml/
COPY font/ ./font/
COPY .env .

ENV PYTHONPATH=/var/task

CMD ["handler.handle"]
