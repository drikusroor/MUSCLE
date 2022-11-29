import logging
import random
from os.path import join
from django.template.loader import render_to_string
from .toontjehoger_1_mozart import toontjehoger_ranks
from .views import Trial, Explainer, Step, Score, Final, StartSession, Playlist, Info
from .views.form import ButtonArrayQuestion, Form
from .views.playback import Playback
from .base import Base
from .util.actions import combine_actions
from .util.strings import non_breaking

logger = logging.getLogger(__name__)


class ToontjeHoger5Tempo(Base):
    ID = 'TOONTJE_HOGER_5_TEMPO'
    TITLE = ""
    SCORE_CORRECT = 20
    SCORE_WRONG = 0

    @classmethod
    def first_round(cls, experiment, participant):
        """Create data for the first experiment rounds."""

        # 1. Explain game.
        explainer = Explainer(
            instruction="Timing en tempo",
            steps=[
                Step(
                    "Je krijgt dadelijk twee verschillende uitvoeringen van hetzelfde stuk te horen."),
                Step("Eén wordt op de originele snelheid (tempo) afgespeeld, terwijl de ander iets is versneld of vertraagd."),
                Step(
                    "Kan jij horen welke het origineel is?"),
                Step("Let hierbij vooral op de timing van de muzikanten.")
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
            return cls.get_round(session, rounds_passed)

        # Round 2
        if rounds_passed < session.experiment.rounds:
            return combine_actions(*cls.get_score(session), *cls.get_round(session, rounds_passed))

        # Final
        return combine_actions(*cls.get_final_round(session))

    @classmethod
    def get_random_section_pair(cls, session, genre):
        """
          - session: current Session
          - genre: (C)lassic (J)azz (R)ock

          Voor de track: genereer drie random integers van 1-5 (bijv. [4 2 4])
          Plak deze aan de letters C, J en R (bijv. [C4, J2, R4])
          Voor het paar: genereer drie random integers van 1-2 (bijv. [1 2 2])
          Plak deze aan de letter P (bijv. P1, P2, P2)
          We willen zowel de originele als de veranderde versie van het paar. Dus combineer
          bovenstaande met OR en CH (bijv. “C4_P1_OR”, “C4_P1_CH”, etc.)
        """
        # Previous tags
        previous_tags = [
            result.section.tag for result in session.result_set.all()]

        # Get a random, unused track
        # Loop until there is a valid tag
        iterations = 0
        valid_tag = False
        tag_base = ""
        tag_original = ""
        while(not valid_tag):
            track = random.choice([1, 2, 3, 4, 5])
            pair = random.choice([1, 2])
            tag_base = "{}{}_P{}_".format(genre.upper(), track, pair, )
            tag_original = tag_base + "OR"
            if not (tag_original in previous_tags):
                valid_tag = True

            # Failsafe: prevent infinite loop
            # If this happens, just reuse a track
            iterations += 1
            if iterations > 10:
                valid_tag = True

        tag_changed = tag_base + "CH"

        section_original = session.section_from_any_song(
            filter_by={'tag': tag_original, 'group': "or"})

        if not section_original:
            raise Exception(
                "Error: could not find original section: {}".format(tag_original))

        section_changed = cls.get_section_changed(
            session=session, tag=tag_changed)

        sections = [section_original, section_changed]
        random.shuffle(sections)
        return sections

    @classmethod
    def get_section_changed(cls, session, tag):
        section_changed = session.section_from_any_song(
            filter_by={'tag': tag, 'group': "ch"})
        if not section_changed:
            raise Exception(
                "Error: could not find changed section: {}".format(tag))
        return section_changed

    @classmethod
    def get_round(cls, session, round):
        # Get sections
        genre = ["C", "J", "R"][round % 3]

        sections = cls.get_random_section_pair(session, genre)
        section_original = sections[0] if sections[0].group == "or" else sections[1]

        # Create result
        result_pk = cls.prepare_result(
            session, section=section_original, expected_response="A" if sections[0].id == section_original.id else "B")

        # Player
        play_config = {
            'label_style': 'ALPHABETIC',
        }

        playback = Playback(
            sections, player_type=Playback.TYPE_MULTIPLAYER, play_config=play_config)

        # Question
        question = ButtonArrayQuestion(
            question="Welk fragment wordt in het originele tempo afgespeeld?",
            key='pitch',
            choices={
                "A": "A",
                "B": "B",
            },
            submits=True,
            result_id=result_pk
        )
        form = Form([question])

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
    def calculate_score(cls, result, data, scoring_rule, form_element):
        return cls.SCORE_CORRECT if result.expected_response == result.given_response else cls.SCORE_WRONG

    @classmethod
    def get_section_pair_from_result(cls, result):
        section_original = result.section

        if section_original is None:
            raise Exception(
                "Error: could not get section from result")

        tag_changed = section_original.tag.replace("OR", "CH")
        section_changed = cls.get_section_changed(
            session=result.session, tag=tag_changed)

        if section_changed is None:
            raise Exception(
                "Error: could not get changed section for tag: {}".format(
                    tag_changed))

        return (section_original, section_changed)

    @ classmethod
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

            section_original, section_changed = cls.get_section_pair_from_result(
                last_result)

            # Create feedback message
            # - Track names are always the same
            # - Artist could be different
            if section_original.artist == section_changed.artist:
                feedback += " Je hoorde {}, in beide fragmenten uitgevoerd door {}.".format(
                    last_result.section.name, last_result.section.artist)
            else:
                section_a = section_original if last_result.expected_response == "A" else section_changed
                section_b = section_changed if section_a.id == section_original.id else section_original
                feedback += " Je hoorde {} uitgevoerd door A) {} en B) {}.".format(
                    section_a.name, non_breaking(section_a.artist), non_breaking(section_b.artist))

        # Return score view
        config = {'show_total_score': True}
        score = Score(session, config=config, feedback=feedback).action()
        return [score]

    @ classmethod
    def get_final_round(cls, session):

        # Finish session.
        session.finish()
        session.save()

        # Score
        score = cls.get_score(session)

        # Final
        final_text = "Dat bleek toch even lastig!"
        if session.final_score >= session.experiment.rounds * 0.8 * cls.SCORE_CORRECT:
            final_text = "Goed gedaan! Jouw timing is uitstekend!"
        elif session.final_score >= session.experiment.rounds * 0.5 * cls.SCORE_CORRECT:
            final_text = "Goed gedaan! Jouw timing is best OK!"

        final = Final(
            session=session,
            final_text=final_text,
            rank=toontjehoger_ranks(session),
            button={'text': 'Wat hebben we getest?'}
        ).action()

        # Info page
        body = render_to_string(
            join('info', 'toontjehoger', 'experiment5.html'))
        info = Info(
            body=body,
            heading="Timing en tempo",
            button_label="Terug naar ToontjeHoger",
            button_link="/toontjehoger"
        ).action()

        return [*score, final, info]
