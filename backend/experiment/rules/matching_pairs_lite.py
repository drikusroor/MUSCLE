import random

from django.utils.translation import gettext_lazy as _

from .matching_pairs import MatchingPairsGame
from experiment.actions import Final, Playlist, Info
from experiment.actions.utils import final_action_with_optional_button


class MatchingPairsLite(MatchingPairsGame):
    ID = 'MATCHING_PAIRS_LITE'
    num_pairs = 8
    show_animation = False
    score_feedback_display = 'small-bottom-right'
    contact_email = 'aml.tunetwins@gmail.com'
    randomize = True

    def first_round(self, experiment):     
        # 2. Choose playlist.
        playlist = Playlist(experiment.playlists.all())
        info = Info('',
                    heading='Press start to enter the game',
                    button_label='Start')
        return [
            playlist, info
        ]
    
    def next_round(self, session):
        if session.rounds_passed() < 1:
            trial = self.get_matching_pairs_trial(session)
            return [trial]
        else:
            return final_action_with_optional_button(session, final_text='End of the game', title='Score', button_text='Back to dashboard')

    def select_sections(self, session):
        pairs = list(session.playlist.section_set.order_by().distinct(
            'group').values_list('group', flat=True))
        if self.randomize:
            random.shuffle(pairs)
        selected_pairs = pairs[:self.num_pairs]
        originals = session.playlist.section_set.filter(
            group__in=selected_pairs, tag='Original')
        degradations = session.playlist.section_set.exclude(tag='Original').filter(
            group__in=selected_pairs)
        if degradations:
            return list(originals) + list(degradations)
        else:
            return list(originals) + list(originals)
