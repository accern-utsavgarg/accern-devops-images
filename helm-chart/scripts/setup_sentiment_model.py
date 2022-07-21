import sys

import accern_xyme

# Deploy the sentiment model dags.
# Assumes that xyme config is already set (setup_config.py)
# Assumes that the sentiment model binary is saved to
# /tmp/sentiment_model.zip (download_dag_zips_from_s3.py)


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
print("Deploy infer dag", DAG_INFER_URI)

DAG_INFER = XYME.get_dag(DAG_INFER_URI)
DAG_INFER.upload_full_dag_zip("/tmp/INFER_DAG.zip")

################################################
# Training
# used for training new models
################################################

DAG_TRAIN_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_TRAIN_ID}"
print("Deploy training dag", DAG_TRAIN_URI)

DAG_TRAIN = XYME.get_dag(DAG_TRAIN_URI)
DAG_TRAIN.upload_full_dag_zip("/tmp/TRAIN_DAG.zip")

################################################
# Kafka
################################################

DAG_KAFKA_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_KAFKA_ID}"
print("Deploy kafka dag", DAG_KAFKA_URI)

DAG_KAFKA = XYME.get_dag(DAG_KAFKA_URI)
DAG_KAFKA.upload_full_dag_zip("/tmp/KAFKA_DAG.zip")

print(XYME.create_kafka_error_topic())

if DAG_KAFKA.get_kafka_group()["reset"] != "earliest":
    DAG_KAFKA.set_kafka_group(reset="earliest")

print(DAG_KAFKA.scale_worker(2))
