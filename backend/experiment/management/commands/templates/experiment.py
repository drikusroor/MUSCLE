from typing import Final
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

from experiment.actions import Consent, BooleanQuestion, Explainer, Final, Form, Playlist, Step, Trial
from experiment.actions.playback import Autoplay
from experiment.questions.demographics import EXTRA_DEMOGRAPHICS
from experiment.questions.utils import question_by_key
from experiment.rules.base import Base
from result.utils import prepare_result
from section.models import Playlist


class NewExperiment(Base):
    ID = 'NEW_EXPERIMENT'
    contact_email = 'info@example.com'

    def __init__(self):

        # Add your questions here
        self.questions = [
            question_by_key('dgf_gender_identity'),
            question_by_key('dgf_generation'),
            question_by_key('dgf_musical_experience', EXTRA_DEMOGRAPHICS),
            question_by_key('dgf_country_of_origin'),
            question_by_key('dgf_education', drop_choices=[
                            'isced-2', 'isced-5'])
        ]


    def first_round(self, experiment):
        # 1. Informed consent
        rendered = render_to_string('consent/consent_new_experiment.html')
        consent = Consent(rendered, title=_(
            'Informed consent'), confirm=_('I agree'), deny=_('Stop'))
        
        # 2. Choose playlist (only relevant if there are multiple playlists the participant can choose from)
        playlist = Playlist(experiment.playlists.all())

        # 3. Explainer
        explainer = Explainer(
            instruction='Welcome to this new experiment',
            steps=[
                Step(description=_('Please read the instructions carefully')),
                Step(description=_('Next step of explanation')),
                Step(description=_('Another step of explanation')),
            ],
            step_numbers=True
        )
        
        return [
            consent,
            playlist,
            explainer
        ]
    
    def next_round(self, session):
        # ask any questions defined in the admin interface
        actions = self.get_questionnaire(session)

        if actions:
            return actions
        elif session.rounds_complete():
            # we have as many results as rounds in this experiment
            # finish session and show Final view
            session.finish()
            session.save()
            return [Final()]
        else:
            return self.get_trial(session)

    def get_trial(self, session):
        # define a key, by which responses to this trial can be found in the database
        key = 'test_trial'
        # get a random section
        section = session.section_from_any_song()
        question = BooleanQuestion(
            question=_(
                "Do you like this song?"),
            key=key,
            result_id=prepare_result(key, session, section=section),
            submits=True
        )
        form = Form([question])
        playback = Autoplay([section])
        view = Trial(
            playback=playback,
            feedback_form=form,
            title=_('Test experiment'),
            config={
                'response_time': section.duration,
                'listen_first': True
            }
        )
        return view
    