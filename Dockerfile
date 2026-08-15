FROM python:3.12-alpine

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

EXPOSE 5007

# The server console script is not installed by packaging, so invoke main directly.
ENTRYPOINT ["python3", "-c", "from concord232.main import main; main()"]
CMD ["--serial", "/dev/ttyUSB0", "--listen", "0.0.0.0", "--port", "5007"]
