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

def log_move_event(uid,game,is_over):

    gain_list = []
    round = game.current_round

    pos = 0
    for i in range(len(round)):
        r = round[i]
        if r['opened'] == True:
            pos = pos + 1
        gain_list.append(str(r['gain']))

    # print 'Gain List: {0} User Id: {1} Depth: {2}'.format(gain_list,uid,pos)
    # print(game['round_no'])

    gain_str = ' '.join(gain_list)
    round_no = game['round_no']
    if(round_no == 1):
        msg ='------------------------New Start Here-------------------------------'
        msg += '\r\t\t\t\t\t\t\tUser Id: {0} Game Id: {1} Depth: {2} Gain List: {3} round:{4}'.format(uid, game.id, pos, gain_str,round_no)
    else:
         msg = '\r\t\t\t\t\t\t\tUser Id: {0} Game Id: {1} Depth: {2} Gain List: {3} round:{4}'.format(uid, game.id, pos, gain_str,round_no)

    if is_over == True:
        msg += '\r\t\t\t\t\t\t\toooooooooooooooooooooooooo Complete Log ooooooooooooooooooooooooooooooo\r\r'

    event_logger.info(msg=msg)