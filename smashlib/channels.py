""" smashlib.channels
"""

C_CD_EVENT = 'cd'
C_POST_RUN_CELL = 'post_run_cell'
C_POST_RUN_INPUT = 'post_run_input'
C_SMASH_INIT_COMPLETE = 'smash_init_complete'
C_UPDATE_PROMPT_REQUEST = 'udpate_prompt_request'


# just examples
def post_run_cell(bus, finished_input_interpretted):
    print 'prc-',finished_input_interpretted

def post_run_input(bus, raw_finished_input):
    print 'pri-', raw_finished_input
