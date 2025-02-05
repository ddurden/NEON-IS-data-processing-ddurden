from pachyderm_sdk import Client
from pachyderm_sdk.api import pfs, pps, transaction
from google.protobuf import json_format
from dataclasses import fields
import environs
from urllib.parse import urlparse
import yaml
import json
from pathlib import Path
import io
import os

def setup_client(pachd_address:str, pach_token:str):
    
    # Example of how to create a robot token with the required permissions for pipeline updates
    #   pachctl auth get-robot-token testrunner
    #   pachctl auth set project default repoOwner robot:testrunner
    
    pach_url = urlparse(pachd_address)
    host = pach_url.hostname
    port = pach_url.port
    if port is None:
        port = 80
    if pach_url.scheme == "https" or pach_url.scheme == "grpcs":
        tls = True
    else:
        tls = False
    return Client(host=host, port=port, tls=tls, auth_token=pach_token) 

def pipeline_files_from_pipe_lists(paths):
    # Get the list of pipeline yamls to update
    # paths: a list of type Path or string indicating the directory that contains pipeline specifications. 
    # Note that the directory must contain a pipe_list_*.txt file listing the pipeline specs that make up the DAG. 
    # The order of paths as well as the internal ordering of the pipe_list_*.txt file should be in the order they should be loaded into pachyderm.
    pipeline_files=[]
    for path in paths:
        print(f'Looking in directory {path} for pipeline list (pipe_list_*.txt)')
        # Load the ordered pipeline list 
        for pipe_list_file in Path(path).rglob('pipe_list_*.txt'):
            print(f'Reading pipeline list {pipe_list_file}')
            with open(pipe_list_file, 'r') as file:
                for line in file:
                    line=line.rstrip('\n').strip()
                    if len(line) > 0:
                        pipeline_files.append(Path(path,line))
            break # Only read the first pipe_list file (should only be 1)
    print(f'{len(pipeline_files)} total pipelines will be updated')
    return(pipeline_files)


def create_pipeline_reqs(pipeline_files):
    # Read in pipeline yaml files and convert to pipeline request
    print('Reading pipeline files and generating pipeline requests')
    pipeline_reqs = {}
    for pipe_yaml in pipeline_files:
        print(f'Reading {pipe_yaml}')
        with open(pipe_yaml, 'r') as file:
            pipe = yaml.safe_load(file)
            pipe["update"] = True
            pipe_json = json.dumps(pipe)
            pipe_req = pps.CreatePipelineRequest().from_json(pipe_json) 
            pipeline_reqs[pipe["pipeline"]["name"]] = pipe_req
    return pipeline_reqs


def update_dag(client, pipeline_reqs, transaction: bool):
    # Deploy pipeline updates to Pachyderm. Note - if the pipeline does not exist, it will be created.
    if transaction is True:
        print('Using transaction')
        with client.transaction.transaction() as t:
            for pipe in pipeline_reqs:
                print(f'Updating {pipe}')
                pipeline_req = pipeline_reqs[pipe]
                client.pps.create_pipeline(
                    **{f.name: getattr(pipeline_req, f.name)
                    for f in fields(pipeline_req)}
                )
    else:
        for pipe in pipeline_reqs:
            print(f'Updating {pipe}')
            pipeline_req = pipeline_reqs[pipe]
            client.pps.create_pipeline(
                **{f.name: getattr(pipeline_req, f.name)
                for f in fields(pipeline_req)}
            )

        
def main():
    env = environs.Env()
    pachd_address = os.environ["PACHD_ADDRESS"] # e.g. "grpcs://pachd.nonprod.gcp.neoninternal.org:443"
    pach_token = os.environ["PACH_TOKEN"] # auth token (string). Needs repoOwner roles
    paths = env.list('PATHS') # list of path strings to the directories with pipeline specs to update
    transaction = env.bool('TRANSACTION',True) # Do updates within a single transaction (recommended)
    
    # Get the list of pipeline yamls to update
    # pipeline_files must be in the desired order of loading to pachyderm. Thus, the order of paths as well as the internal ordering of the pipe_list file matters.
    pipeline_files = pipeline_files_from_pipe_lists(paths)

    # Create pipeline requests from pipeline files
    pipeline_reqs = create_pipeline_reqs(pipeline_files)

    # Connect to pachyderm    
    client = setup_client(pachd_address,pach_token)

    # Update the pipelines
    update_dag(client,pipeline_reqs,transaction)
    


if __name__ == "__main__":
    main()


