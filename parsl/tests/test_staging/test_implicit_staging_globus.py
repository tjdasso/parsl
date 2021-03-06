import pytest

import parsl
from parsl.app.app import App
from parsl.data_provider.files import File
from parsl.tests.configs.local_threads_globus import config, remote_writeable

local_config = config


@App('python')
def sort_strings(inputs=[], outputs=[]):
    with open(inputs[0].filepath, 'r') as u:
        strs = u.readlines()
        strs.sort()
        with open(outputs[0].filepath, 'w') as s:
            for e in strs:
                s.write(e)


@pytest.mark.local
def test_stage_in_globus():
    """Test stage-in for a file coming from a remote Globus endpoint

    Prerequisite:
        unsorted.txt must already exist at the specified endpoint
    """

    unsorted_file = File('globus://03d7d06a-cb6b-11e8-8c6a-0a1d4c5c824a/unsorted.txt')

    # Create a local file for output data
    sorted_file = File('sorted.txt')

    f = sort_strings(inputs=[unsorted_file], outputs=[sorted_file])

    f.result()


@pytest.mark.local
def test_stage_in_out_globus():
    """Test stage-in then stage-out to/from Globus

    Prerequisite:
        unsorted.txt must already exist at the specified endpoint
        the specified output endpoint must be writeable
    """

    unsorted_file = File('globus://03d7d06a-cb6b-11e8-8c6a-0a1d4c5c824a/unsorted.txt')

    # Create a local file for output data
    sorted_file = File(remote_writeable + "/sorted.txt")

    f = sort_strings(inputs=[unsorted_file], outputs=[sorted_file])

    # wait for both the app to complete, and the stageout DataFuture to complete.
    # It isn't clearly defined whether we need to wait for both, or whether
    # waiting for one is sufficient, but at time of writing this test,
    # neither is sufficient (!) - see issue #778 - and instead this test will
    # sometimes pass even though stageout is not working.

    f.result()
    f.outputs[0].result()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Count of apps to launch")
    args = parser.parse_args()

    if args.debug:
        parsl.set_stream_logger()

    test_stage_in_out_globus()
