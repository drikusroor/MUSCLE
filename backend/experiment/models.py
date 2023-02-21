import copy

from django.db import models
from django.utils import timezone
from experiment.rules import EXPERIMENT_RULES
from experiment.standards.iso_languages import ISO_LANGUAGES

language_choices = [(key, ISO_LANGUAGES[key]) for key in ISO_LANGUAGES.keys()]
language_choices[0] = ('', 'Unset')

class ExperimentSeries(models.Model):
    """ A model to allow nesting multiple experiments into a 'parent' experiment """
    name = models.CharField(max_length=64, default='')
    # first experiments in a test series, in fixed order
    first_experiments = models.JSONField(blank=True, null=True, default=dict)
    random_experiments = models.JSONField(blank=True, null=True, default=dict)
    # last experiments in a test series, in fixed order
    last_experiments = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.name

class Experiment(models.Model):
    """Root entity for configuring experiments"""

    playlists = models.ManyToManyField('section.Playlist', blank=True)
    name = models.CharField(db_index=True, max_length=64)
    slug = models.CharField(db_index=True, max_length=64, unique=True)
    active = models.BooleanField(default=True)
    rounds = models.PositiveIntegerField(default=10)
    bonus_points = models.PositiveIntegerField(default=0)
    rules = models.CharField(default="", max_length=64)
    language = models.CharField(
        default="", blank=True, choices=language_choices, max_length=2)
    experiment_series = models.ForeignKey(ExperimentSeries, on_delete=models.SET_NULL,
                                          blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def session_count(self):
        """Number of sessions"""
        return self.session_set.count()

    session_count.short_description = "Sessions"

    def playlist_count(self):
        """Number of playlists"""
        return self.playlists.count()

    playlist_count.short_description = "Playlists"

    def current_participants(self):
        """Get distinct list of participants"""
        participants = {}
        for session in self.session_set.all():
            participants[session.participant.id] = session.participant
        return participants.values()

    def export_admin(self):
        """Export data for admin"""
        return {
            'exportedAt': timezone.now().isoformat(),
            'experiment': {
                'id': self.id,
                'name': self.name,
                'sessions': [session.export_admin() for session in self.session_set.all()],
                'participants': [
                    participant.export_admin() for participant in self.current_participants()
                ]
            },
        }

    def export_table(self, session_keys, result_keys, export_options):
        """Export filtered tabular data for admin        
            session_keys : session fieldnames to be included
            result_keys : result fieldnames to be included
            export_options : export options (see admin/forms.py)
        """
        rows = []  # a list of dictionaries
        fieldnames = set()  # keep track of all potential fieldnames
        result_prefix = ''
        for session in self.session_set.all():
            profile = session.participant.export_admin()
            session_finished = session.finished_at.isoformat() if session.finished_at else None
            # Get data for all potential session fields
            full_row = {
                'experiment_id': self.id,
                'experiment_name': self.name,
                'participant_id': profile['id'],
                'participant_country': profile['country_code'],
                'participant_access_info': profile['access_info'],
                'session_start': session.started_at.isoformat(),
                'session_end': session_finished,
                'final_score': session.final_score
            }
            row = {}
            # Add the selected sessions fields
            for session_key in session_keys:
                row[session_key] = full_row[session_key]
            # Add profile data if selected
            if 'export_profile' in export_options:
                row.update(profile['profile'])
            # Add session data
            if session.json_data != '':
                if 'session_data' in export_options:
                    # Convert json session data to csv columns if selected
                    if 'convert_session_json' in export_options:
                        row.update(session.load_json_data())
                    else:
                        row['session_data'] = session.load_json_data()
            fieldnames.update(row.keys())
            if session.result_set.count() == 0:
                # some sessions may have only profile questions
                rows.append(row)
            else:
                result_counter = 1
                # Create new row for each result
                if 'wide_format' in export_options:
                    this_row = copy.deepcopy(row)
                for result in session.result_set.all():
                    # Add all results to one row
                    if not 'wide_format' in export_options:
                        this_row = copy.deepcopy(row)
                    # Get data for al potential result fields
                    full_result_data = {
                        'section_name': result.section.name if result.section else None,
                        'result_created_at': result.created_at.isoformat(),
                        'result_score': result.score,
                        'result_comment': result.comment,
                        'expected_response': result.expected_response,
                        'given_response': result.given_response
                    }
                    result_data = {}
                    # Add counter for single row / wide format
                    if 'wide_format' in export_options:
                        result_prefix = str(result_counter).zfill(3) + '-'
                        # add the selected result fields
                        for result_key in result_keys:
                            result_data[(result_prefix + result_key)
                                        ] = full_result_data[result_key]
                    else:
                        # add the selected result fields
                        for result_key in result_keys:
                            result_data[result_key] = full_result_data[result_key]
                    # Add result data
                    if result.json_data != '':
                        # convert result json data to csv columns if selected
                        if 'convert_result_json' in export_options:
                            if 'decision_time' in export_options:
                                result_data[result_prefix + 'decision_time'] = result.load_json_data().get(
                                    'decision_time', '')
                            if 'result_config' in export_options:
                                result_data[result_prefix + 'result_config'] = result.load_json_data().get(
                                    'config', '')
                        else:
                            if 'result_config' in export_options:
                                result_data[result_prefix +
                                            'result_data'] = result.load_json_data()
                    this_row.update(result_data)
                    fieldnames.update(result_data.keys())
                    result_counter += 1
                    # Append row for long format
                    if not 'wide_format' in export_options:
                        rows.append(this_row)
                # Append row for wide format
                if 'wide_format' in export_options:
                    rows.append(this_row)
        return rows, list(fieldnames)

    def get_rules(self):
        """Get rules class to be used for this session"""
        return EXPERIMENT_RULES[self.rules]

    def max_score(self):
        """Get max score from all sessions with a positive score"""
        score = self.session_set.filter(
            final_score__gte=0).aggregate(models.Max('final_score'))
        if 'final_score__max' in score:
            return score['final_score__max']

        return 0