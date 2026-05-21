FROM public.ecr.aws/lambda/python:3.12

COPY lambda/requirements.txt .
RUN pip install -r requirements.txt

COPY lambda/handler.py .

CMD ["handler.lambda_handler"]
