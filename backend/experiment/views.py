import logging

from django.http import Http404, JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate

from .models import Experiment
from session.models import Session
from participant.utils import get_or_create_participant

logger = logging.getLogger(__name__)

# Experiment

def get_experiment(request, slug):
    """Get experiment data from active experiment with given :slug"""
    # get experiment
    try:
        experiment = Experiment.objects.get(slug=slug, active=True)
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")

    series_data = request.session.get('experiment_series')
    if experiment.experiment_series and series_data:
        # we are in the middle of a test battery
        try:
            session = Session.objects.get(
                pk=series_data.get('session_id'),
                experiment=experiment
            )
        except Session.DoesNotExist:
            # delete session data and reload
            del request.session['experiment_series']
            return redirect('/experiment/id/{}/'.format(slug), request)

        # convert non lists to list
        next_round = session.experiment_rules().next_round(session)
        if not isinstance(next_round, list):
            next_round = [next_round]

        data = {
            'session': {
                'id': session.id,
                'playlist': session.playlist.id,
                'json_data': session.load_json_data(),
            },
            'next_round': next_round
        }
        return JsonResponse(data, json_dumps_params={'indent': 4})

    class_name = ''
    if request.LANGUAGE_CODE.startswith('zh'):
        class_name = 'chinese'

    if experiment.language:
        activate(experiment.language)

    # get current participant
    participant = get_or_create_participant(request)

    # create data
    experiment_data = {
        'id': experiment.id,
        'slug': experiment.slug,
        'name': experiment.name,
        'class_name': class_name,  # can be used to override style
        'rounds': experiment.rounds,
        'playlists': [
            {'id': playlist.id, 'name': playlist.name}
            for playlist in experiment.playlists.all()
        ],
        'next_round': experiment.get_rules().first_round(experiment, participant),
        'loading_text': _('Loading')
    }

    response = JsonResponse(experiment_data, json_dumps_params={'indent': 4})
    if experiment.language:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, experiment.language)
    else:
        # avoid carrying over language cookie from other experiments
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, None)
    return response