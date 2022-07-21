import accern_xyme

print("Downloading Dag Zips from S3")

accern_xyme.XYMEClient.download_s3_from_file(
    ["/tmp/INFER_DAG.zip", "/tmp/KAFKA_DAG.zip", "/tmp/TRAIN_DAG.zip"],
    "download_dag_zips_from_s3.json")
