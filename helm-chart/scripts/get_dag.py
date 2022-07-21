import argparse
import json
import os
from typing import Optional, TypedDict

import accern_xyme

ArgsDict = TypedDict('ArgsDict', {
    "identifier": str,
    "dag": bool,
    "host": str,
    "token": Optional[str],
    "namespace": Optional[str],
})


def parse_args() -> ArgsDict:
    parser = argparse.ArgumentParser(
        prog=f"python {os.path.basename(os.path.dirname(__file__))}",
        description="retrieves dag information")
    parser.add_argument(
        "identifier",
        type=str,
        help="either the dag URI or a solution id")
    parser.add_argument(
        "--dag",
        action="store_true",
        help="if set, only the dag URI will be printed")
    parser.add_argument(
        "--host",
        type=str,
        default="http://xyme-monitor:8080/",
        help="specifies the monitor URL prefix")
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="the XYME token. inferred if unspecified")
    parser.add_argument(
        "--namespace",
        type=str,
        default=None,
        help="the XYME namespace. default if unspecified")

    args = parser.parse_args()
    return {
        "identifier": args.identifier,
        "dag": args.dag,
        "host": args.host,
        "token": args.token,
        "namespace": args.namespace,
    }


def get_xyme(
        host: Optional[str],
        token: Optional[str],
        namespace: Optional[str]) -> accern_xyme.XYMEClient:
    if host is None:
        host = accern_xyme.DEFAULT_URL
    if token is None:
        token = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")
    if namespace is None:
        namespace = accern_xyme.DEFAULT_NAMESPACE
    return accern_xyme.create_xyme_client(host, token, namespace)


def interpret_identifier(identifier: str) -> str:
    if "://" in identifier:
        # dag URI
        return identifier
    # solutionID
    solid = identifier.replace("-", "")
    return f"s3://accern-ml-forecast@aws/dag/b{solid}"


def get_dag() -> None:
    args = parse_args()
    dag_uri = interpret_identifier(args["identifier"])
    if args["dag"]:
        print(dag_uri)
    else:
        xyme = get_xyme(args["host"], args["token"], args["namespace"])
        dag_hnd = xyme.get_dag(dag_uri)
        print(json.dumps(dag_hnd.get_def(), indent=2, sort_keys=True))


if __name__ == "__main__":
    get_dag()
