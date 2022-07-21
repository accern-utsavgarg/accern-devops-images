import sys
import uuid

import accern_xyme
import pandas as pd

print(sys.argv)
XYME_HOST = sys.argv[1] if len(sys.argv) > 1 else "http://xyme-monitor:8080/"

XYME_SERVER_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")

print(XYME_HOST, XYME_SERVER_TOKEN)
XYME = accern_xyme.create_xyme_client(XYME_HOST, XYME_SERVER_TOKEN)

DAG_IDS = accern_xyme.XYMEClient.load_json("setup_sentiment_model.json")
DAG_INFER_ID = DAG_IDS["infer"]

if "" in [f"{DAG_INFER_ID}".strip()]:
    raise ValueError("dag infer id config value is empty.")

DAG_INFER_URI = f"s3://accern-ml-nlp@aws/dag/b{DAG_INFER_ID}"
print("infer dag", DAG_INFER_URI)

accern_xyme.XYMEClient.download_s3_from_file(
    ["/tmp/verify_infer.csv", "/tmp/verify_infer_1.csv"],
    "verify_inference.json")

DAG_INFER = XYME.get_dag(DAG_INFER_URI)


def tests(dag_infer: accern_xyme.DagHandle) -> None:
    simple = dag_infer.dynamic_list(
        [f"Apple announces new battery. {uuid.uuid4().hex}"])
    print(simple)
    assert len(simple) == 1
    float(simple[0])

    df_all_agree = pd.read_csv("/tmp/verify_infer.csv").copy()
    print(df_all_agree.head())

    df_50_agree = pd.read_csv("/tmp/verify_infer_1.csv").copy()
    print(df_50_agree.head())

    df_all_agree["model_pred_reg"] = dag_infer.dynamic_list(
        df_all_agree["Sentence"].tolist())

    df_50_agree["model_pred_reg"] = dag_infer.dynamic_list(
        df_50_agree["Sentence"].tolist())

    print(df_all_agree.head())
    print(df_50_agree.head())

    th = 26

    df_all_agree["model_pred"] = "negative"
    df_all_agree.loc[df_all_agree["model_pred_reg"] > -th, "model_pred"] = \
        "neutral"
    df_all_agree.loc[df_all_agree["model_pred_reg"] >= th, "model_pred"] = \
        "positive"

    df_all_agree["ground_truth"] = "negative"
    df_all_agree.loc[df_all_agree["Sentiment"] == 1, "ground_truth"] = \
        "neutral"
    df_all_agree.loc[df_all_agree["Sentiment"] == 2, "ground_truth"] = \
        "positive"

    perf_all_agree = \
        (df_all_agree["model_pred"] == df_all_agree["ground_truth"]).mean()

    df_50_agree["model_pred"] = "negative"
    df_50_agree.loc[df_50_agree["model_pred_reg"] > -th, "model_pred"] = \
        "neutral"
    df_50_agree.loc[df_50_agree["model_pred_reg"] > th, "model_pred"] = \
        "positive"

    df_50_agree["ground_truth"] = "negative"
    df_50_agree.loc[df_50_agree["Sentiment"] == 1, "ground_truth"] = "neutral"
    df_50_agree.loc[df_50_agree["Sentiment"] == 2, "ground_truth"] = "positive"

    perf_50_agree = \
        (df_50_agree["model_pred"] == df_50_agree["ground_truth"]).mean()

    print(perf_all_agree, perf_50_agree)
    pd.testing.assert_series_equal(
        pd.Series([perf_all_agree]),
        pd.Series([0.9350706713780919]))

    pd.testing.assert_series_equal(
        pd.Series([perf_50_agree]),
        pd.Series([0.8142798184069335]))


tests(DAG_INFER)
