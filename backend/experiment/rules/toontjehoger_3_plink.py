import logging
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from .views import Plink, Explainer, Step, Score, Final, StartSession, Playlist, Info
from .views.form import ChoiceQuestion, RadiosQuestion, Form, DropdownQuestion, RadiosQuestion
from .views.playback import Playback
from .base import Base
from os.path import join
from .util.actions import combine_actions

logger = logging.getLogger(__name__)


class ToontjeHoger3Plink(Base):
    ID = 'TOONTJE_HOGER_3_PLINK'
    TITLE = _("Toontje Hoger")
    SCORE_MAIN_CORRECT = 50
    SCORE_MAIN_WRONG = -10
    SCORE_EXTRA_CORRECT = 15
    SCORE_EXTRA_WRONG = 0

    @classmethod
    def first_round(cls, experiment):
        """Create data for the first experiment rounds."""

        # 1. Explain game.
        explainer = Explainer(
            instruction="Uitleg",
            steps=[
                Step(_("Luister naar een heel kort muziekfragment.")),
                Step(
                    _("Ken je het nummer? Noem de juiste artiest en titel!")),
                Step(
                    _("Weet je het niet? Beantwoord dan extra vragen over de tijdsperiode en emotie van het nummer."))
            ],
            button_label=_("Start")

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
            return cls.get_plink_round(session)

        # Round 2-6
        if rounds_passed <= 5:
            return combine_actions(*cls.get_score(session), *cls.get_plink_round(session))

        # Final
        return combine_actions(*cls.get_final_round(session))

    @classmethod
    def get_score_message(cls, session):
        last_result = session.last_result()

        if not last_result:
            logger.error("No last result")
            return ""

        data = last_result.load_json_data()

        # Section
        section = last_result.section
        if not section:
            logger.error("Result without section")
            return ""

        # Main question
        main_question = Plink.extract_main_question(data)

        if main_question:
            if main_question == last_result.expected_response:
                return "Je hoorde inderdaad {} van {}".format(section.name, section.artist)
            
            return "Helaas, volgende keer beter"

        extra_questions = Plink.extract_extra_questions(data)
        if extra_questions:
            # Section details
            section_details = section.group.split(";")
            time_period = section_details[0] if len(section_details) >= 1 else "?"
            emotion = section_details[1] if len(section_details) >= 2 else "?"
            feedback = "Het nummer komt uit de {} en de emotie is {}.".format(time_period, emotion)
            return feedback

        return ""

    @classmethod
    def get_score(cls, session):
        feedback = cls.get_score_message(session)

        # Return score view
        config = {'show_total_score': True}
        score = Score(session, config=config, feedback=feedback).action()

        return [score]

    @classmethod
    def get_plink_round(cls, session):

        # Config
        # -----------------

        # Get all song sections
        all_sections = session.all_sections()
        choices = {}
        for section in all_sections:
            label = section.song_label()
            choices[section.pk] = label

        # Get section to recognize
        section = session.section_from_unused_song()
        if section == None:
            raise Exception("Error: could not find section")

        expected_response = section.pk
        result_pk = cls.prepare_result(
            session, section=section, expected_response=expected_response)

        # Plink round
        # --------------------
        extra_questions = [cls.get_optional_question1(
            session), cls.get_optional_question2(session)]

        plink = Plink(
            section=section,
            title=cls.TITLE,
            result_id=result_pk,
            main_question=_('Noem de artiest en de titel van het nummer'),
            choices=choices,
            submit_label=_("Volgende"),
            dont_know_label=_("Ik weet het niet"),
            extra_questions=extra_questions,
        ).action()

        return [plink]

    @classmethod
    def get_optional_question1(cls, session):

        # Config
        # -----------------

        # Question
        periods = ["60's", "70's", "80's", "90's", "00's", "10's", "20's"]
        period_choices = {}
        for period in periods:
            period_choices[period] = period

        question = RadiosQuestion(
            question=_('Wanneer is het nummer uitgebracht?'),
            key='time_period',
            choices=period_choices,
            submits=False
        )

        return question.action()

    @classmethod
    def get_optional_question2(cls, session):

        # Question
        emotions = ['vrolijk', 'droevig', 'boosheid', 'angst', 'tederheid']
        emotion_choices = {}
        for emotion in emotions:
            emotion_choices[emotion] = emotion.capitalize()

        question = RadiosQuestion(
            question=_('Welke emotie past bij dit nummer?'),
            key='emotion',
            choices=emotion_choices,
            submits=True
        )

        return question.action()

    @classmethod
    def calculate_score(cls, result, form_element, data):
        """
        Calculate score, based on the data field

        e.g. only main question answered
        {
            main_question: "100",
            extra_questions: []
        }

        e.g. only main question answered
        {
            main_question: "",
            extra_questions: ["60s","vrolijk"]
        }

        """
        main_question = Plink.extract_main_question(data)

        # Participant guessed the artist/title:
        if main_question != "":
            result.given_response = main_question
            result.save()
            return cls.SCORE_MAIN_CORRECT if result.expected_response == result.given_response else cls.SCORE_MAIN_WRONG

        # Handle extra questions data
        extra_questions = Plink.extract_extra_questions(data)
        if extra_questions:
            section = result.section
            if section is None:
                logger.error("Error: No section on result")
                return 0

            score = 0

            # Check if the given answers
            # e.g section.group = 60s;vrolijk (time_period;emotion)
            for answer in extra_questions:
                score += cls.SCORE_EXTRA_CORRECT if answer in section.group else cls.SCORE_EXTRA_WRONG

            return score

        # Should not happen
        logger.error("Error: could not calculate score")
        return 0

    @classmethod
    def get_final_round(cls, session):

        # Finish session.
        session.finish()
        session.save()

        # Score
        score = cls.get_score(session)

        # Info page
        body = render_to_string(
            join('info', 'toontjehoger', 'experiment3.html'))
        info = Info(body=body, heading=_("Muziekherkenning"),
                    continue_button=_("Volgende")).action()

        # Final
        final_text = _("Goed gedaan, jouw muziekherkenning is uitstekend!") if session.final_score >= 4 * \
            cls.SCORE_MAIN_CORRECT else _("Wellicht nog een poging wagen? Er is ruimte voor verbetering.")
        final = Final(
            session=session,
            final_text=final_text,
            rank=cls.rank(session),
            button={'link': 'https://www.amsterdammusiclab.nl',
                    'text': 'Terug naar ToontjeHoger'}
        ).action()

        return [*score, info, final]

