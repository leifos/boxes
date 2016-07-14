# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from models import UserProfile, MaxHighScore, GameExperiment

from game import create_and_start_game, store_game, retrieve_game, end_game

from log import log_move_event

gameId = None
access_limit = 10
unlockScore = [0, 0, 0, 0, 0, 0]


def index(request):
    context = RequestContext(request, {})
    return render_to_response('asg/index.html', context)


def howToPlay(request):
    context = RequestContext(request, {})
    return render_to_response('asg/howToPlay.html', context)



def pick(request, username):
    ge = GameExperiment.objects.all()
    user = User.objects.get(username=username)
    mhs = MaxHighScore.objects.filter(user=user)

    lock = [0, 1, 1, 1, 1, 1]
    global unlockScore
    unlockScore = [0, 35, 45, 40, 45, 45]

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
    up = UserProfile.objects.all().extra(select={'total': 'total_points / no_games_played'}).order_by('-total')
    paginator = Paginator(up, 20)
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
    log_move_event(request.user.id, game, True, False)

    global gameId
    gameId = int(num)

    global access_limit
    access_limit = 10

    data = game.get_game_state()
    store_game(session_id, game)
    response = render_to_response('asg/game.html', {'sid': session_id, 'data': data, 'gameId': gameId}, context)
    response.set_cookie('gid', session_id)
    return response


def query(request):
    context = RequestContext(request, {})
    gid = ''
    star_info = [0,0,0]
    star_thisGame = 0
    data = {}
    global access_limit
    access_limit = 10

    if request.COOKIES.has_key('gid'):
        gid = request.COOKIES['gid']
    game = retrieve_game(gid)
    if game:

        log_move_event(request.user.id, game, False, False)


        query_msg = game.issue_query()

        # # check if query success or not
        # if query_msg == True:
        #     log_move_event(request.user.id, game, False, False)

        store_game(gid, game)
        data = game.get_game_state()

    new_high = False
    if game.is_game_over():
        # check if this is a high score
        # update userprofile stats
        log_move_event(request.user.id, game, False, True)
        new_high = end_game(request.user, game)

        if game.id == 6:
            return render_to_response('asg/game.html', {'sid': gid, 'data': data, 'new_high': new_high, 'gameId': gameId,
                                                'query_msg': query_msg,},
                              context)

        star_info = star_game(game.id)
        star_thisGame = star_calculate(data['points'],unlockScore[game.id])

    return render_to_response('asg/game.html', {'sid': gid, 'data': data, 'new_high': new_high, 'gameId': gameId,
                                                'query_msg': query_msg,'starInfo':star_info,'star':star_thisGame},
                              context)


def assess(request):
    context = RequestContext(request, {})
    gid = ''
    star_info = [0,0,0]
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

        store_game(gid, game)
        data = game.get_game_state()

    new_high = False
    if game.is_game_over():
        # check if this is a high score
        # update userprofile stats
        log_move_event(request.user.id, game, False, True)
        new_high = end_game(request.user, game)

        if game.id == 6:
            return render_to_response('asg/game.html',
                              {'sid': gid, 'data': data, 'new_high': new_high, 'access_msg': access_msg,
                               'gameId': gameId},
                              context)

        star_info = star_game(game.id)
        star_thisGame = star_calculate(data['points'],unlockScore[game.id])

    return render_to_response('asg/game.html',
                              {'sid': gid, 'data': data, 'new_high': new_high, 'access_msg': access_msg,
                               'gameId': gameId,'starInfo':star_info,'star':star_thisGame},
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
