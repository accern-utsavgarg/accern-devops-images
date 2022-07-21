import sys

import accern_xyme

# Download the full dag zips to upload to s3 for setting up dags.
# Assumes that xyme config is already set (setup_config.py)

print(sys.argv)
XYME_HOST = sys.argv[1] if len(sys.argv) > 1 else "http://xyme-monitor:8080/"

DAG_IDS = accern_xyme.XYMEClient.load_json("setup_sentiment_model.json")
XYME_SERVER_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")

print(XYME_HOST, XYME_SERVER_TOKEN)
XYME = accern_xyme.create_xyme_client(XYME_HOST, XYME_SERVER_TOKEN)

# Read Config
DAG_INFER_ID = DAG_IDS["infer"]
DAG_TRAIN_ID = DAG_IDS["train"]
DAG_KAFKA_ID = DAG_IDS["kafka"]

SENTIMENT_KEYS = [
    DAG_INFER_ID,
    DAG_TRAIN_ID,
    DAG_KAFKA_ID,
]

if "" in (f"{val}".strip() for val in SENTIMENT_KEYS):
    raise ValueError(f"sentiment model config value is empty. {DAG_IDS}")

################################################
# Inference
# Used for dynamic inference
################################################

DAG_INFER_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_INFER_ID}"
print("Download infer dag", DAG_INFER_URI)

DAG_INFER = XYME.get_dag(DAG_INFER_URI)
DAG_INFER.download_full_dag_zip("/tmp/INFER_DAG.zip")

################################################
# Training
# used for training new models
################################################

DAG_TRAIN_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_TRAIN_ID}"
print("Download training dag", DAG_TRAIN_URI)

DAG_TRAIN = XYME.get_dag(DAG_TRAIN_URI)
DAG_TRAIN.download_full_dag_zip("/tmp/TRAIN_DAG.zip")

################################################
# Kafka
################################################

DAG_KAFKA_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_KAFKA_ID}"
print("Download kafka dag", DAG_KAFKA_URI)

DAG_KAFKA = XYME.get_dag(DAG_KAFKA_URI)
DAG_KAFKA.download_full_dag_zip("/tmp/KAFKA_DAG.zip")
