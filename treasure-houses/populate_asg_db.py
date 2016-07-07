__author__ = 'leif'
from asg_project import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.contrib.auth.models import User
from asg.models import GameExperiment, UserProfile

def add_game_exp(name, config, desc,level=1):
    ge = GameExperiment.objects.get_or_create(name=name, config=config,desc=desc, level=level)
    return ge


def add_player(name, pw):

    email = '{0}@{1}.com'.format(name,name)
    try:
        u = User.objects.get(username=name)
    except:
        u = User(username=name, email=email)
        u.set_password(pw)
        u.save()
        up = UserProfile(user=u)
        up.save()


def main():
    add_game_exp('Wooden House', 1 ,desc='Payoffs are Random.')
    add_game_exp('Coffee Shop', 2 ,desc='Payoffs are High.')
    add_game_exp('Purple Roof' ,3, desc='Payoffs are High, Med or Low.')
    add_game_exp('Sakura' ,4, desc='Payoffs are Random,with information.')
    add_game_exp('Wild Man' ,5, desc='Payoffs are High,with information.')
    add_game_exp('Rainbow' ,6, desc='Payoffs are High, Med or Low,with information.')

    add_player('jill','test')
    add_player('jim','test')

if __name__ == "__main__":
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "asg_project.settings")
    main()