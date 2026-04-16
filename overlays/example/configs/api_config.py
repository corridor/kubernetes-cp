import datetime
import os


SQLALCHEMY_DATABASE_URI = (
    "postgresql://user:password@postgres.example.internal:5432/example"
)
CONFIGS = "/opt/corridor/config"
DATABASE_DIR = "/opt/corridor/databases"
CELERY_BROKER_URL = "redis://redis.shared.svc.cluster.local:6379/0"
CELERY_RESULT_BACKEND = "redis://redis.shared.svc.cluster.local:6379/0"
REST_API_SERVER_URL = "/corr-api"
NOTEBOOK_CONFIGS = {"link": "/jupyter/hub/login"}
OUTPUT_DATA_LOCATION = "/opt/corridor/data/results/{}.parquet"
OUTPUT_DATA_FORMAT = "parquet"
API_URL = "http://corridor-app-service:5002/corr-api/"
TASK_TIME_LIMIT = datetime.timedelta(hours=20).total_seconds()
TASK_SOFT_TIME_LIMIT = datetime.timedelta(hours=20).total_seconds()

os.environ["PYSPARK_PYTHON"] = "/opt/corridor/venv/bin/python3"
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--driver-memory 2G --executor-memory 2G --master local[2] pyspark-shell"
)


APP_PROCESSES = 1

# ENABLE_WORKSPACE = "true"
# ALLOW_OTP_LOGIN = "true"