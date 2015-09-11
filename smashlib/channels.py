""" smashlib.channels
"""

C_CHANGE_DIR = 'cd'
C_PRE_RUN_CELL = 'pre_run_cell'
C_POST_RUN_CELL = 'post_run_cell'
C_POST_RUN_INPUT = 'post_run_input'
C_REHASH_EVENT = 'rehash'
C_SMASH_INIT_COMPLETE = 'smash_init_complete'
C_UPDATE_PROMPT_REQUEST = 'udpate_prompt_request'
C_COMMAND_FAIL = 'fail'
C_DOT_CMD = 'dot_cmd'
C_FILE_INPUT = 'file_input'
C_URL_INPUT = 'url_input'

# venv plugin uses this stuff but
# much of it has to be renamed.
C_POST_ACTIVATE = 'post_activate_venv'
C_PRE_ACTIVATE = 'pre_activate_venv'
C_POST_DEACTIVATE = 'post_deactivate_venv'
C_PRE_DEACTIVATE = 'pre_deactivate'

# just examples
# def post_run_cell(bus, finished_input_interpretted):
#    print 'prc-', finished_input_interpretted
#
#
# def post_run_input(bus, raw_finished_input):
#    print 'pri-', raw_finished_input
