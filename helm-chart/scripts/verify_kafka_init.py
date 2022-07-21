import sys
import time

import accern_xyme

print(sys.argv)
XYME_HOST = sys.argv[1] if len(sys.argv) > 1 else "http://xyme-monitor:8080/"

XYME_SERVER_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")

print(XYME_HOST, XYME_SERVER_TOKEN)
XYME = accern_xyme.create_xyme_client(XYME_HOST, XYME_SERVER_TOKEN)

DAG_IDS = accern_xyme.XYMEClient.load_json("setup_sentiment_model.json")
DAG_KAFKA_ID = DAG_IDS["kafka"]

if "" in [f"{DAG_KAFKA_ID}".strip()]:
    raise ValueError("dag kafka id config value is empty.")

DAG_KAFKA_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_KAFKA_ID}"
print("kafka dag", DAG_KAFKA_URI)

accern_xyme.XYMEClient.download_s3_from_file(
    ["/tmp/verify_kafka.json"], "verify_kafka_init.json")

DAG_KAFKA = XYME.get_dag(DAG_KAFKA_URI)


def tests(
        xyme: accern_xyme.XYMEClient,
        dag_kafka: accern_xyme.DagHandle) -> None:
    bench_obj = xyme.load_json("/tmp/verify_kafka.json")

    dag_kafka.post_kafka_objs([bench_obj])

    print("offset a", dag_kafka.get_kafka_offsets(alive=True))
    time.sleep(60.0)
    print("offset b", dag_kafka.get_kafka_offsets(alive=True))

    print("run next: python verify_kafka_result.py")


tests(XYME, DAG_KAFKA)
