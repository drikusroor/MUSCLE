from .hooked import Hooked
import random
from django.utils.translation import gettext_lazy as _
from experiment.actions import SongSync, Trial
from experiment.actions.playback import Autoplay
from experiment.actions.form import BooleanQuestion, Form
from experiment.actions.styles import STYLE_BOOLEAN_NEGATIVE_FIRST
from result.utils import prepare_result


class Eurovision2020(Hooked):
    """Rules for the Eurovision 2020 version of the Hooked experiment.

    Based on the MBCS internship projects of Ada Orken and and Leanne Kuiper.
    """

    ID = 'EUROVISION_2020'
    play_method = 'BUFFER'

    def plan_sections(self, session):
        """Set the plan of tracks for a session.

        N.B. Assumes exactly one segment each of tags 1, 2, and 3 per song!
        """

        # Which songs are available?
        free_song_set = set(session.playlist.song_ids({'tag__lt': 3}))
        old_new_song_set = set(session.playlist.song_ids({'tag__gt': 0}))

        # How many sections do we need?
        n_old = round(0.17 * session.experiment.rounds)
        n_new = round(0.33 * session.experiment.rounds) - n_old
        n_free = session.experiment.rounds - 2 * n_old - n_new

        # Assign songs.
        old_songs = random.sample(old_new_song_set, k=n_old)
        free_songs = random.sample(free_song_set - set(old_songs), k=n_free)
        new_songs = \
            random.sample(
                free_song_set - set(old_songs + free_songs),
                k=n_new
            )

        # Assign tags for Block 2. Technically 1 and 2 are also OK for the
        # 'free' sections in Block 1, but it is easier just to set tag 0.
        free_tags = [0] * n_free
        old_tags_1 = random.choices([1, 2], k=n_old)
        condition = random.choice(['same', 'different', 'karaoke'])
        if condition == 'karaoke':
            old_tags_2 = [3] * n_old
            new_tags = [3] * n_new
        # Reverse tags 1 and 2 for the 'different' condition.
        elif condition == 'different':
            old_tags_2 = [3 - tag for tag in old_tags_1]
            new_tags = random.choices([1, 2], k=n_new)
        else:  # condition == 'same'
            old_tags_2 = old_tags_1
            new_tags = random.choices([1, 2], k=n_new)

        # Randomise.
        permutation_1 = random.sample(range(n_free + n_old), n_free + n_old)
        permutation_2 = random.sample(range(n_old + n_new), n_old + n_new)
        plan = {
            'n_song_sync': n_free + n_old,
            'n_heard_before': n_old + n_new,
            'condition': condition,
            'songs': (
                [(free_songs + old_songs)[i] for i in permutation_1]
                + [(old_songs + new_songs)[i] for i in permutation_2]
            ),
            'tags': (
                [(free_tags + old_tags_1)[i] for i in permutation_1]
                + [(old_tags_2 + new_tags)[i] for i in permutation_2]
            ),
            'novelty': (
                [(['free'] * n_free + ['old'] * n_old)[i]
                 for i in permutation_1]
                + [(['old'] * n_old + ['new'] * n_new)[i]
                   for i in permutation_2]
            )
        }

        # Save, overwriting existing plan if one exists.
        session.save_json_data({'plan': plan})
        # session.save() is required for persistence
        session.save()
    
    def next_song_sync_action(self, session):
        """Get next song_sync section for this session."""

        # Load plan.
        next_round_number = session.get_next_round()
        try:
            plan = session.load_json_data()['plan']
            songs = plan['songs']
            tags = plan['tags']
        except KeyError as error:
            print('Missing plan key: %s' % str(error))
            return None

        # Get section.
        section = None
        if next_round_number <= len(songs) and next_round_number <= len(tags):
            section = \
                session.section_from_song(
                    songs[next_round_number - 1],
                    {'tag': tags[next_round_number - 1]}
                )
        if not section:
            print("Warning: no next_song_sync section found")
            section = session.section_from_any_song()
        key = 'song_sync'
        result_id = prepare_result(key, session, section=section, scoring_rule='SONG_SYNC')
        return SongSync(
            key=key,
            section=section,
            title=self.get_trial_title(session, next_round_number),
            config = {'play_method': self.play_method},
            result_id=result_id
        )
    
    def next_heard_before_action(self, session):
        """Get next heard_before action for this session."""

        # Load plan.
        next_round_number = session.get_next_round()
        try:
            plan = session.load_json_data()['plan']
            songs = plan['songs']
            tags = plan['tags']
            novelty = plan['novelty']
        except KeyError as error:
            print('Missing plan key: %s' % str(error))
            return None

        # Get section.
        section = None
        if next_round_number <= len(songs) and next_round_number <= len(tags):
            section = \
                session.section_from_song(
                    songs[next_round_number - 1],
                    {'tag': tags[next_round_number - 1]}
                )
        if not section:
            print("Warning: no heard_before section found")
            section = session.section_from_any_song()

        playback = Autoplay(
            sections = [section],
            show_animation=True,
            ready_time=3,
            preload_message=_('Get ready!')
        )
        expected_result = int(novelty[next_round_number - 1] == 'old')
        # create Result object and save expected result to database
        result_pk = prepare_result('heard_before', session, section=section, expected_response=expected_result, scoring_rule='REACTION_TIME')
        form = Form([BooleanQuestion(
            key='heard_before',
            choices={
                'new': _("No"),
                'old': _("Yes"),
            },
            question=_("Did you hear this song in previous rounds?"),
            result_id=result_pk,
            style=STYLE_BOOLEAN_NEGATIVE_FIRST,
            submits=True)])
        config = {      
            'auto_advance': True,
            'decision_time': self.timeout
        }
        trial = Trial(
            title=self.get_trial_title(session, next_round_number),
            playback=playback,
            feedback_form=form,
            config=config,
        )
        return trial

