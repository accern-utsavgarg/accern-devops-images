import os
import sys
import time

import accern_xyme
import pandas as pd

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

DAG_KAFKA = XYME.get_dag(DAG_KAFKA_URI)


def check_accuracy(obj: dict) -> float:
    res = []
    themes = obj.get("article", {}).get("themes", [])
    for _, theme in enumerate(themes):
        theme_obj = theme.get("entity", {})
        if "slops" in theme_obj:
            truth = [
                slop.get("truth_sentiment", "error")
                for slop in theme_obj.get("slops", [])
            ]
            res.append(pd.DataFrame({
                "Sentiment": truth,
                "model_pred": theme_obj["sentiment"],
            }))
    th = 26

    data = pd.concat(res, axis=0)
    data["model_pred_sent"] = "negative"
    data.loc[data["model_pred"] > -th, "model_pred_sent"] = "neutral"
    data.loc[data["model_pred"] >= th, "model_pred_sent"] = "positive"

    data["ground_truth"] = "negative"
    data.loc[data["Sentiment"] == 1, "ground_truth"] = "neutral"
    data.loc[data["Sentiment"] == 2, "ground_truth"] = "positive"
    return (data["model_pred_sent"] == data["ground_truth"]).mean()


def tests(
        xyme: accern_xyme.XYMEClient,
        dag_kafka: accern_xyme.DagHandle) -> None:
    errs = xyme.read_kafka_errors("current")
    print("errors", len(errs))
    if errs:
        tmp_path = os.path.join("/tmp", "kafka_errors.txt")
        with open(tmp_path, "a") as fout:
            for err in errs:
                print(err, file=fout)
        print(f"see {tmp_path} for details")

    response = None
    start_time = time.monotonic()
    timeout = 30 * 60  # 30min
    offset = "current"
    while response is None:
        msg = dag_kafka.read_kafka_output(offset)
        if msg is not None:
            for obj in msg:
                assert isinstance(obj, dict)
                if obj["pipelineId"] == "phrasebank":
                    response = obj
                    break
        if time.monotonic() - start_time > timeout:
            raise ValueError(
                "waiting for results timed out. run this script again")

    perf_bench = check_accuracy(response)
    print(perf_bench)
    pd.testing.assert_series_equal(
        pd.Series([perf_bench]),
        pd.Series([0.9350706713780919]))


tests(XYME, DAG_KAFKA)
