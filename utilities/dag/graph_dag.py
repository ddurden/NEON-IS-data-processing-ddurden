#!/usr/bin/env python3
import argparse
from pathlib import Path

from dag.dag_manager import DagManager


def main(end_node_specification: str, specification_dir: str):
    """
    Graph a DAG.

    :param end_node_specification: The end node pipeline specification file.
    :param specification_dir: A directory containing the DAG pipeline specification files.
    :return:
    """
    manager = DagManager(Path(end_node_specification), Path(specification_dir))
    manager.graph_dag()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--end_node_spec')
    arg_parser.add_argument('--spec_dir')
    args = arg_parser.parse_args()
    main(args.end_node_spec, args.spec_dir)
