import argparse
import os
from typing import Optional, Tuple, TypedDict

import accern_xyme

ArgsDict = TypedDict('ArgsDict', {
    "host": str,
    "token": Optional[str],
    "dag": Optional[str],
    "topic": Optional[str],
    "namespace": Optional[str],
    "target": int,
})


def parse_args() -> ArgsDict:
    parser = argparse.ArgumentParser(
        prog=f"python {os.path.basename(os.path.dirname(__file__))}",
        description="scales a worker up / down")
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
        "--dag",
        type=str,
        default=None,
        help="the dag to scale as URI")
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="the dag to scale as kafka topic")
    parser.add_argument(
        "--namespace",
        type=str,
        default=None,
        help="the XYME namespace. if unspecified will be inferred")
    parser.add_argument(
        "target",
        type=int,
        help="indicates that this process is started internally")

    args = parser.parse_args()
    return {
        "host": args.host,
        "token": args.token,
        "dag": args.dag,
        "topic": args.topic,
        "namespace": args.namespace,
        "target": int(args.target),
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
    print(f"Logging into XYME: host={host} namespace={namespace}")
    return accern_xyme.create_xyme_client(host, token, namespace)


def get_dag_uri(
        namespace: Optional[str],
        dag: Optional[str],
        topic: Optional[str]) -> Tuple[Optional[str], str]:
    if dag is not None:
        return namespace, dag
    if topic is None:
        raise ValueError("must specify either dag URI or kafka topic")
    orig_topic = topic
    nochop = True
    for chop in ["xyme-output-", "xyme-input-"]:
        if topic.startswith(chop):
            topic = topic[len(chop):]
            nochop = False
            break
    if nochop:
        raise ValueError(f"unknown kafka topic format: {orig_topic}")
    segs = topic.split("-")
    if len(segs) < 4:
        raise ValueError(f"kafka topic too short: {orig_topic}")
    if namespace is None:
        namespace = segs[0]
    connector = segs[1]
    location = None
    address = None
    uid = None
    pos = len(segs) - 1
    while pos > 1:
        cur = segs[pos]
        if uid is None:
            if len(cur) == 32:
                uid = cur
        elif address is None:
            address = cur
        elif location is None:
            location = cur
        else:
            location = f"{cur}-{location}"
        pos -= 1
    if address is None or uid is None:
        raise ValueError(f"missing address or UUID: {orig_topic}")
    if location is None:
        location = ""
    else:
        location = f"{location}@"
    return namespace, f"{connector}://{location}{address}/dag/b{uid}"


def scale() -> None:
    args = parse_args()
    namespace, dag = get_dag_uri(args["namespace"], args["dag"], args["topic"])
    xyme = get_xyme(args["host"], args["token"], namespace)
    target = args["target"]
    if target < 0:
        raise ValueError(f"invalid scaling {target}")
    if target == 0:
        msg = "down"
    elif target == 1:
        msg = f"to {target} worker"
    else:
        msg = f"to {target} workers"
    print(f"scaling {dag} {msg}")
    dag_hnd = xyme.get_dag(dag)
    cur_num = -1
    while cur_num != target:
        if cur_num >= 0:
            print(f"...achieved only {cur_num} out of {target} workers")
        cur_num = dag_hnd.scale_worker(target)
    if cur_num > 1:
        print(f"all {cur_num} workers are ready")
    elif cur_num > 0:
        print("one worker is ready")
    else:
        print("all workers scaled down")


if __name__ == "__main__":
    scale()
