from django.utils.translation import gettext as _

class Final:  # pylint: disable=too-few-public-methods
    """
    Provide data for a final view

    Relates to client component: Final.js
    """

    ID = 'FINAL'

    RANKS = {
        'PLASTIC': {'text': _('plastic'), 'class': 'plastic'},
        'BRONZE':  {'text': _('bronze'), 'class': 'bronze'},
        'SILVER': {'text': _('silver'), 'class': 'silver'},
        'GOLD': {'text': _('gold'), 'class': 'gold'},
        'PLATINUM': {'text': _('platinum'), 'class': 'platinum'},
        'DIAMOND': {'text': _('diamond'), 'class': 'diamond'}
    }

    def __init__(self, session, title=_("Final score"), final_text=None,
            button=None, rank=None, show_social=False, 
            show_profile_link=False, show_participant_link=False,
            show_participant_id_only=False
        ):
        self.session = session
        self.title = title
        self.final_text = final_text
        self.button = button
        self.rank = rank
        self.show_social = show_social
        self.show_profile_link = show_profile_link
        self.show_participant_link = show_participant_link
        self.show_participant_id_only = show_participant_id_only

    def action(self):
        """Get data for final action"""
        return {
            'view': Final.ID,
            'score': self.session.total_score(),
            'rank': self.rank,
            'final_text': self.final_text,
            'button': self.button,
            'points': _("points"),
            'action_texts': {
                'play_again': _('Play again'),
                'profile': _('My profile'),
                'all_experiments': _('All experiments')
            },
            'title': self.title,
            'show_social': self.show_social,
            'show_profile_link': self.show_profile_link,
            'show_participant_link': self.show_participant_link,
            'participant_id_only': self.show_participant_id_only
        }
