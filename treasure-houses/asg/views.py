# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from models import UserProfile, MaxHighScore, GameExperiment

from game import create_and_start_game, store_game, retrieve_game, end_game

from log import log_move_event
from random import randint

gameId = None
access_limit = 10
unlockScore = [0, 0, 0, 0, 0, 0]

treasure_display_list = []
current_display_list = []
access_display_list = []
noise = 0


def index(request):
    context = RequestContext(request, {})
    return render_to_response('asg/index.html', context)


def howToPlay(request):
    context = RequestContext(request, {})
    return render_to_response('asg/howToPlay.html', context)


def about(request):
    context = RequestContext(request, {})
    return render_to_response('asg/about.html', context)


def pick(request, username):
    ge = GameExperiment.objects.all()
    user = User.objects.get(username=username)
    mhs = MaxHighScore.objects.filter(user=user)

    lock = [0, 1, 1, 1, 1, 1]
    global unlockScore
    unlockScore = [0, 32, 47, 37, 35, 50]

    maxHighScore = [0, 0, 0, 0, 0, 0]

    count = 0
    for s in mhs:
        if mhs:
            maxHighScore[count] = s.points
            count += 1

    star = [star_calculate(maxHighScore[0], unlockScore[1]),
            star_calculate(maxHighScore[1], unlockScore[2]),
            star_calculate(maxHighScore[2], unlockScore[3]),
            star_calculate(maxHighScore[3], unlockScore[4]),
            star_calculate(maxHighScore[4], unlockScore[5]),
            0
            ]

    for g in ge:

        if g.id == 1 and maxHighScore[0] >= unlockScore[1]:
            lock[1] = 0
        if g.id == 2 and maxHighScore[1] >= unlockScore[2]:
            lock[2] = 0
        if g.id == 3 and maxHighScore[2] >= unlockScore[3]:
            lock[3] = 0
        if g.id == 4 and maxHighScore[3] >= unlockScore[4]:
            lock[4] = 0
        if g.id == 5 and maxHighScore[4] >= unlockScore[5]:
            lock[5] = 0

    zipped_data = zip(ge, lock, unlockScore, maxHighScore, star)
    context = RequestContext(request, {})

    return render_to_response('asg/pick.html', {'ge': ge, 'lock': lock, 'zipped_data': zipped_data}, context)


def leaderboard(request):
    context = RequestContext(request, {})
    # up = UserProfile.objects.all().extra(select={'get_average_points'}).order_by('-total')
    up_list = list(UserProfile.objects.all())
    up_list = sorted(up_list, key=lambda x: 0 if x.no_games_played == 0 else x.total_points / float(x.no_games_played),
                     reverse=True)

    paginator = Paginator(up_list, 20)
    page = request.GET.get('page')
    try:
        players = paginator.page(page)
    except PageNotAnInteger:
        players = paginator.page(1)
    except EmptyPage:
        players = paginator.page(paginator.num_pages)

    return render_to_response('asg/leaderboard.html', {'players': players}, context)


def startgame(request, num):
    context = RequestContext(request, {})
    session_id = request.session._get_or_create_session_key()
    game = create_and_start_game(int(num))

    global gameId
    gameId = int(num)

    global access_limit
    access_limit = 10

    nextTreasureNo = 10 - access_limit

    data = game.get_game_state()
    store_game(session_id, game)

    # gems coating here
    gain_list = []
    round = game.current_round
    for i in range(len(round)):
        r = round[i]
        gain_list.append(str(r['gain']))

    global treasure_display_list
    treasure_display_list = []

    global current_display_list
    current_display_list = gems_coating(gameId, gain_list)
    global access_display_list
    access_display_list = current_display_list

    rounds_list = data['round']
    zipped_data = zip(current_display_list, rounds_list)

    log_move_event(request.user.id, game, current_display_list, True, False)

    # ------------------------------------------

    global noise
    noise = 3

    response = render_to_response('asg/game.html',
                                  {'sid': session_id, 'data': data, 'zipped_data': zipped_data, 'gameId': gameId,
                                   'next': nextTreasureNo, 'noise': noise}, context)
    response.set_cookie('gid', session_id)
    return response


def query(request):
    context = RequestContext(request, {})
    gid = ''
    star_info = [0, 0, 0]
    star_thisGame = 0
    data = {}



    if request.COOKIES.has_key('gid'):
        gid = request.COOKIES['gid']
    game = retrieve_game(gid)
    if game:

        gain_list = []
        round = game.current_round

        for i in range(len(round)):
            r = round[i]
            gain_list.append(str(r['gain']))

        global treasure_display_list
        treasure_display_list = []

        # global current_display_list
        # current_display_list = gems_coating(gameId, gain_list)

        log_move_event(request.user.id, game, current_display_list, False, False)

        query_msg = game.issue_query()

        current_gain_list = []
        current_round = game.current_round
        for i in range(len(current_round)):
            r = current_round[i]
            current_gain_list.append(str(r['gain']))

        # # check if query success or not
        # if query_msg == True:
        #     log_move_event(request.user.id, game, False, False)
        nextTreasureNo = 10 - access_limit
        if query_msg == True:
            global access_limit
            access_limit = 10
            nextTreasureNo = 10 - access_limit

            global current_display_list
            current_display_list = gems_coating(game.id, current_gain_list)


        store_game(gid, game)
        data = game.get_game_state()

        rounds_list = data['round']
        zipped_data = zip(current_display_list, rounds_list)

        global access_display_list
        access_display_list = current_display_list


    if game.id != 6:
        star_info = star_game(game.id)
        star_thisGame = star_calculate(data['points'], unlockScore[game.id])


    global noise
    noise = 2

    new_high = False
    if game.is_game_over():
        # check if this is a high score
        # update userprofile stats
        log_move_event(request.user.id, game, current_display_list, False, True)
        new_high = end_game(request.user, game)
        global noise
        noise = 4

        if game.id == 6:
            return render_to_response('asg/game.html',
                                      {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'new_high': new_high,
                                       'gameId': gameId,
                                       'query_msg': query_msg, 'next': nextTreasureNo, 'noise': noise},
                                      context)

    if data['tokens'] == 1 and query_msg == False and access_limit <= 0:
        special_msg = True
        return render_to_response('asg/game.html',
                                  {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'gameId': gameId,
                                   'new_high': new_high, 'special_msg': special_msg,
                                   'gameId': gameId, 'next': None, 'noise': noise},
                                  context)

    return render_to_response('asg/game.html',
                              {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'new_high': new_high,
                               'gameId': gameId,
                               'query_msg': query_msg, 'starInfo': star_info, 'star': star_thisGame,
                               'next': nextTreasureNo, 'noise': noise},
                              context)


def assess(request):
    context = RequestContext(request, {})
    gid = ''
    star_info = [0, 0, 0]
    star_thisGame = 0
    if request.COOKIES.has_key('gid'):
        gid = request.COOKIES['gid']

    data = {}
    access_msg = True

    game = retrieve_game(gid)
    if game:
        global access_limit
        if access_limit > 0:
            game.examine_document()
            access_limit -= 1
        else:
            access_msg = False

        nextTreasureNo = 10 - access_limit

        store_game(gid, game)
        data = game.get_game_state()

        rounds_list = data['round']
        zipped_data = zip(access_display_list, rounds_list)
        # -----------------------------------------
    if game.id != 6:
        star_info = star_game(game.id)
        star_thisGame = star_calculate(data['points'], unlockScore[game.id])

    global noise
    noise = 1

    new_high = False
    if game.is_game_over():
        # check if this is a high score
        # update userprofile stats
        log_move_event(request.user.id, game, current_display_list, False, True)
        new_high = end_game(request.user, game)
        global noise
        noise = 4

        if game.id == 6:
            return render_to_response('asg/game.html',
                                      {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'gameId': gameId,
                                       'new_high': new_high, 'access_msg': access_msg,
                                       'gameId': gameId, 'next': nextTreasureNo, 'noise': noise},
                                      context)

    if data['tokens'] == 1 and access_msg == False:
        special_msg = True
        return render_to_response('asg/game.html',
                                  {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'gameId': gameId,
                                   'new_high': new_high, 'special_msg': special_msg,
                                   'gameId': gameId, 'next': nextTreasureNo, 'noise': noise},
                                  context)

    return render_to_response('asg/game.html',
                              {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'new_high': new_high,
                               'access_msg': access_msg,
                               'gameId': gameId, 'starInfo': star_info, 'star': star_thisGame, 'next': nextTreasureNo,
                               'noise': noise},
                              context)


def endGame(request):
    context = RequestContext(request, {})
    gid = ''
    star_info = [0, 0, 0]
    star_thisGame = 0
    data = {}
    global access_limit
    access_limit = 10

    nextTreasureNo = 10 - access_limit

    if request.COOKIES.has_key('gid'):
        gid = request.COOKIES['gid']
    game = retrieve_game(gid)
    if game:

        # # check if query success or not
        # if query_msg == True:
        #     log_move_event(request.user.id, game, False, False)

        # gems coating here
        gain_list = []
        round = game.current_round
        for i in range(len(round)):
            r = round[i]
            gain_list.append(str(r['gain']))

        global treasure_display_list
        treasure_display_list = []

        # global current_display_list
        # current_display_list = gems_coating(gameId, gain_list)

        log_move_event(request.user.id, game, current_display_list, False, True)
        store_game(gid, game)
        data = game.get_game_state()
        data['gameover'] = True

        rounds_list = data['round']
        zipped_data = zip(current_display_list, rounds_list)

    if game.id != 6:
        star_info = star_game(game.id)
        star_thisGame = star_calculate(data['points'], unlockScore[game.id])
        new_high = False

    # check if this is a high score
    # update userprofile stats
    log_move_event(request.user.id, game, current_display_list, False, True)
    new_high = end_game(request.user, game)

    global noise
    noise = 4

    if game.id == 6:
        return render_to_response('asg/game.html',
                                  {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'new_high': new_high,
                                   'gameId': gameId,
                                   'next': nextTreasureNo, 'noise': noise},
                                  context)

    return render_to_response('asg/game.html',
                              {'sid': gid, 'data': data, 'zipped_data': zipped_data, 'new_high': new_high,
                               'gameId': gameId,
                               'starInfo': star_info, 'star': star_thisGame,
                               'next': nextTreasureNo, 'noise': noise},
                              context)


def profile_page(request, username):
    context = RequestContext(request, {})
    user = User.objects.get(username=username)
    if user:
        user_profile = user.get_profile()
        high_scores = MaxHighScore.objects.filter(user=user)

        combined_points = 0
        mhs = MaxHighScore.objects.filter(user=user)
        for scores in mhs:
            combined_points = combined_points + scores.points

        user_profile.combined_points = combined_points

        return render_to_response('asg/profile.html', {'player': user,
                                                       'profile': user_profile,
                                                       'scores': high_scores, 'game_scores': mhs}, context)
    else:
        return HttpResponse('User not found')


def star_calculate(maxHighScore, unlockScore):
    if maxHighScore <= unlockScore / 3:
        return 0
    if maxHighScore > unlockScore / 3 and maxHighScore <= 2 * unlockScore / 3:
        return 1
    if maxHighScore > 2 * unlockScore / 3 and maxHighScore < unlockScore:
        return 2
    if maxHighScore >= unlockScore:
        return 3
    return 0


def star_game(gameId):
    gid = int(gameId)
    if gameId == 6:
        return
    else:
        star = [0, 0, 0]
        star[0] = int(unlockScore[gid] / 3)
        star[1] = int(2 * unlockScore[gid] / 3)
        star[2] = int(unlockScore[gid])
        return star


def display_decider(number,a,b,c,d,e,f,g,h):
    if number >= 1 and number <= a:
        return e
    if number >= a+1 and number <=a+b:
        return f
    if number >= a+b+1 and number <=a+b+c:
        return g
    if number >= a+b+c+1 and number <=a+b+c+d:
        return h

def gems_coating(gameId, gain_list):
    print 'Actual Gain list: '
    print gain_list
    if gameId <= 3:
        global treasure_noinfo_list
        treasure_noinfo_list = ['-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1']

        return treasure_noinfo_list
    else:
        for g in gain_list:
            # 3 Gems(75%,15%,8%,2%) possibility for Gems(3,2,1,0)
            if g == '3':
                random_number = get_random_number()
                d = display_decider(random_number,2,8,15,75,'0','1','2','3')
                treasure_display_list.append(d)

            # 2 Gems(12%,74%,12%,2%) possibility for Gems(3,2,1,0)
            if g == '2':
                random_number = get_random_number()
                d = display_decider(random_number,2,12,74,12,'0','1','2','3')
                treasure_display_list.append(d)

            # 1 Gems(2%,12%,74%,12%) possibility for Gems(3,2,1,0)
            if g == '1':
                random_number = get_random_number()
                d = display_decider(random_number,2,12,74,12,'3','2','1','0')
                treasure_display_list.append(d)

            # 0 Gems(2%,8%,15%,75%) possibility for Gems(3,2,1,0)
            if g == '0':
                random_number = get_random_number()
                d = display_decider(random_number,2,8,15,75,'3','2','1','0')
                treasure_display_list.append(d)

        return treasure_display_list


def get_random_number():
    r1 = randint(1, 100)
    r2 = randint(1, 100)
    r3 = randint(1, 100)
    r4 = randint(1, 100)
    r5 = randint(1, 100)
    r6 = randint(1, 100)
    r7 = randint(1, 100)
    r8 = randint(1, 100)
    r9 = randint(1, 100)
    r10 = randint(1, 100)
    random_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
    number_decider = randint(1, 10)
    random_number = random_list[number_decider - 1]
    print random_number
    return random_number
