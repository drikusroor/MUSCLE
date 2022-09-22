import logging
import random
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from random import randint
from .views import Trial, Explainer, Step, Score, Final, StartSession, Playlist, Info, HTML
from .views.form import ButtonArrayQuestion, ChoiceQuestion, Form, DropdownQuestion
from .views.playback import Playback
from .base import Base
from os.path import join
from .util.actions import combine_actions

logger = logging.getLogger(__name__)


class ToontjeHoger4Absolute(Base):
    ID = 'TOONTJE_HOGER_4_ABSOLUTE'
    TITLE = ""
    SCORE_CORRECT = 20
    SCORE_WRONG = 0
    PLAYLIST_ITEMS = 13

    @classmethod
    def first_round(cls, experiment, participant):
        """Create data for the first experiment rounds."""

        # 1. Explain game.
        explainer = Explainer(
            instruction="Absoluut gehoor",
            steps=[
                Step(
                    "Je gaat zo luisteren naar fragmenten muziek die je misschien herkent als de intro van een tv programma of serie."),
                Step(
                    "Van ieder fragment kan je twee versies luisteren. Eén hiervan is het origineel. De andere hebben we een beetje hoger of lager gemaakt."),
                Step("Kan jij horen welke van de twee versies precies zo hoog of laag is als je 'm kent? Welke is het origineel?"),
            ],
            button_label="Start"

        ).action(step_numbers=True)

        # 2. Choose playlist.
        playlist = Playlist.action(experiment.playlists.all())

        # 3. Start session.
        start_session = StartSession.action()

        return [
            explainer,
            playlist,
            start_session
        ]

    @classmethod
    def next_round(cls, session, request_session=None):
        """Get action data for the next round"""

        rounds_passed = session.rounds_passed()

        # Round 1
        if rounds_passed == 0:
            # No combine_actions because of inconsistent next_round array wrapping in first round
            return cls.get_round(session)

        # Round 2
        if rounds_passed < session.experiment.rounds:
            return combine_actions(*cls.get_score(session), *cls.get_round(session))

        # Final
        return combine_actions(*cls.get_final_round(session))

    @classmethod
    def get_round(cls, session):
        # Get available section groups
        results = session.result_set.all()
        available_groups = list(map(str, range(1, cls.PLAYLIST_ITEMS)))
        for result in results:
            available_groups.remove(result.section.group)
        print(available_groups)

        # Get sections

        # Original (A)
        section1 = session.section_from_any_song(
            filter_by={'tag': 'a', 'group__in': available_groups})
        if not section1:
            raise Exception(
                "Error: could not find section 1")

        # Changed (B/C)
        variant = random.choice(["b", "c"])
        section2 = session.section_from_any_song(
            filter_by={'tag': variant, 'group': section1.group})
        if not section2:
            raise Exception(
                "Error: could not find section 2 for round")

        # Random section order
        sections = [section1, section2]
        random.shuffle(sections)

        # Create result
        result_pk = cls.prepare_result(
            session, section=section1, expected_response="A" if sections[0].id == section1.id else "B")

        # Player
        play_config = {
            'label_style': 'ALPHABETIC',
        }

        playback = Playback(
            sections, player_type=Playback.TYPE_MULTIPLAYER, play_config=play_config)

        # Question
        question = ChoiceQuestion(
            question="Welk fragment heeft de juiste toonhoogte?",
            key='pitch',
            choices={
                "A": "A",
                "B": "B",
            },
            view='BUTTON_ARRAY',
            submits=True,
            result_id=result_pk
        )
        form = Form([question])
        print(sections[0].tag, sections[0].group,
              sections[1].tag, sections[1].group)

        # Trial
        trial_config = {
            'style': 'neutral',
        }

        trial = Trial(
            config=trial_config,
            playback=playback,
            feedback_form=form,
            title=cls.TITLE,
        ).action()
        return [trial]

    @classmethod
    def calculate_score(cls, result, data, form_element):
        return cls.SCORE_CORRECT if result.expected_response == result.given_response else cls.SCORE_WRONG

    @classmethod
    def get_score(cls, session):
        # Feedback
        last_result = session.last_result()
        feedback = ""
        if not last_result:
            logger.error("No last result")
            feedback = "Er is een fout opgetreden"
        else:
            if last_result.score == cls.SCORE_CORRECT:
                feedback = "Goedzo! Het was inderdaad antwoord {}!".format(
                    last_result.expected_response.upper())
            else:
                feedback = "Helaas! Het juiste antwoord was {}.".format(
                    last_result.expected_response.upper())

            feedback += " Je luisterde naar de intro van {}.".format(
                last_result.section.name)

        # Return score view
        config = {'show_total_score': True}
        score = Score(session, config=config, feedback=feedback).action()
        return [score]

    @classmethod
    def get_final_round(cls, session):

        # Finish session.
        session.finish()
        session.save()

        # Score
        score = cls.get_score(session)

        # Final
        final_text = "Dat bleek toch even lastig!"
        if session.final_score >= session.experiment.rounds * 0.8 * cls.SCORE_CORRECT:
            final_text = "Goed gedaan! Jouw absolute gehoor is uitstekend!"
        elif session.final_score >= session.experiment.rounds * 0.5 * cls.SCORE_CORRECT:
            final_text = "Goed gedaan! Jouw absolute gehoor is best OK!"

        final = Final(
            session=session,
            final_text=final_text,
            rank=cls.rank(session),
            button={'text': 'Wat hebben we getest?'}
        ).action()

        # Info page
        body = render_to_string(
            join('info', 'toontjehoger', 'experiment4.html'))
        info = Info(
            body=body,
            heading="Absoluut gehoor",
            button_label="Terug naar ToontjeHoger",
            button_link="/toontjehoger"
        ).action()

        return [*score, final, info]
