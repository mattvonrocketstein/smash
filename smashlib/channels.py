""" smashlib.channels
"""

C_POST_RUN_CELL = 'post_run_cell'
C_POST_RUN_INPUT = 'post_run_input'


# just examples
def post_run_cell(bus, finished_input_interpretted):
    print 'prc-',finished_input_interpretted

def post_run_input(bus, raw_finished_input):
    print 'pri-', raw_finished_input
