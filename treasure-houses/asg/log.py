__author__ = 'leif'
import os
import logging
import logging.config
import logging.handlers

my_experiment_log_dir = os.getcwd()

event_logger = logging.getLogger('event_log')
event_logger.setLevel(logging.INFO)
event_logger_handler = logging.FileHandler(os.path.join(my_experiment_log_dir, 'move.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
event_logger_handler.setFormatter(formatter)
event_logger.addHandler(event_logger_handler)


def log_move_event(uid, game, display_list, is_start, is_over):
    gain_list = []
    round = game.current_round

    pos = 0
    for i in range(len(round)):
        r = round[i]
        if r['opened'] == True:
            pos = pos + 1
        gain_list.append(str(r['gain']))

    gain_str = ' '.join(gain_list)
    dis_str = ' '.join(display_list)
    round_no = game['round_no']
    action_msg = 'Round_Complete'

    if is_start == True:
        action_msg = 'GAME_START'
        msg = '{0} {1} {2} {3} {4}'.format(uid, game.id, action_msg, game.get_open_cost(), game.get_move_cost())
        event_logger.info(msg=msg)
    elif is_over == True:
        msg = '{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}'.format(uid, game.id,game.get_open_cost(), game.get_move_cost(),game.get_score(),
                                                           action_msg, round_no, pos, gain_str, dis_str)
        event_logger.info(msg=msg)
        action_msg = 'GAME_OVER'
        msg = '{0} {1} {2} {3}'.format(uid, game.id, action_msg, game.get_score())
        event_logger.info(msg=msg)
    else:
        msg = '{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}'.format(uid, game.id,game.get_open_cost(), game.get_move_cost(),game.get_score(),
                                                           action_msg, round_no, pos, gain_str, dis_str)
        event_logger.info(msg=msg)
