import json
from django.http import Http404, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from experiment.models import Session, Experiment, Playlist, Section
from .util.participant import current_participant


@require_POST
def create(request):
    """Create new session for given experiment for current participant"""

    # Current participant
    participant = current_participant(request)

    # Get experiment
    experiment_id = request.POST.get("experiment_id")
    if not experiment_id:
        return HttpResponseBadRequest("experiment_id not defined")
    try:
        experiment = Experiment.objects.get(pk=experiment_id, active=True)
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")

    # Create new session
    session = Session(experiment=experiment, participant=participant)

    # Get playlist
    if experiment.playlists.count() == 1:
        # Skip if there is only one playlist
        session.playlist = experiment.playlists.first()
    else:
        # load playlist from request
        playlist_id = request.POST.get("playlist_id")

        if not playlist_id:
            return HttpResponseBadRequest("playlist_id not defined")

        try:
            playlist = Playlist.objects.get(
                pk=playlist_id, experiment__id=experiment.id)
            session.playlist = playlist
        except Playlist.DoesNotExist:
            raise Http404("Playlist does not exist")

    # Get json_data
    data = request.POST.get("data")
    if data:
        try:
            json.loads(data)
            session.json_data = data
        except ValueError:
            return HttpResponseBadRequest("Invalid data")

    # Save session
    session.save()

    if experiment.experiment_series:
        # save session id to local storage if this experiment contains nested experiments
        request.session.update({'experiment_series': {
            'session_id': session.id,
            'slug': experiment.slug}
        })

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


@require_POST
def result(request):
    """Create a new result for the given session, and return followup action"""

    # Current participant
    participant = current_participant(request)

    # Get session for current participant
    session_id = request.POST.get("session_id")
    if not session_id:
        return HttpResponseBadRequest("session_id not defined")
    try:
        session = Session.objects.get(
            pk=session_id, participant__id=participant.id)
    except Session.DoesNotExist:
        raise Http404("Session does not exist")

    # Prevent creating results when session is finished
    if session.is_finished():
        return HttpResponseServerError("Session has already finished")

    # Create result based on POST data
    json_data = request.POST.get("json_data")
    if not json_data:
        return HttpResponseBadRequest("json_data not defined")

    try:
        result_data = json.loads(json_data)
        # Create a result from the data
        if 'form' in result_data:
            result = session.experiment_rules().handle_results(session, result_data)
        else:
            result = session.experiment_rules().handle_result(session, result_data)
            
        if not result:
            return HttpResponseServerError("Could not create result from data")

    except ValueError:
        return HttpResponseServerError("Invalid data")

    # Get next round for given session
    if request.session.get('experiment_series'):
        # we are in the middle of an experiment series - need to pass in request.session object
        action = session.experiment_rules().next_round(session, request.session)
    else:
        action = session.experiment_rules().next_round(session)
    return JsonResponse(action, json_dumps_params={'indent': 4})


def continue_session(request, session_id):
    """ given a session_id, continue where we left off """
    try:
        session = Session.objects.get(pk=session_id)
    except Session.DoesNotExist:
        raise Http404("Session does not exist")

    # Get next round for given session
    action = session.experiment_rules().next_round(session)
    return JsonResponse(action, json_dumps_params={'indent': 4})


def next_round(request, session_id):
    """
    Fall back to continue an experiment is case next_round data is missing
    This data is normally provided in: result()
    """
    # Current participant
    participant = current_participant(request)

    # Get session
    try:
        session = Session.objects.get(
            pk=session_id, participant__id=participant.id)
    except Session.DoesNotExist:
        raise Http404("Session does not exist")

    # Get next round for given session
    if request.session.get('experiment_series'):
        # we are in the middle of an experiment series - need to pass in request.session object
        action = session.experiment_rules().next_round(session, request.session)
    else:
        # Get next round for given session
        action = session.experiment_rules().next_round(session)

    return JsonResponse(action, json_dumps_params={'indent': 4})
