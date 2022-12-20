from django.test import TestCase

from experiment.models import Experiment, Participant, Result, Session

class ParticipantTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.participant = Participant.objects.create(unique_hash=42)
        cls.experiment = Experiment.objects.create(rules='LISTENING_CONDITIONS', slug='test')
        cls.session = Session.objects.create(
            experiment=cls.experiment,
            participant=cls.participant,
        )
        cls.result1 = Result.objects.create(
            session=cls.session,
            question_key='test1',
            given_response='2 1/2',
            score=2.5,
            is_profile=True
        )
        cls.result2 = Result.objects.create(
            session=cls.session,
            question_key='test2',
            given_response='3',
            is_profile=True
        )
    
    def test_profile(self):
        assert len(self.participant.profile()) == 2
    
    def test_profile_object(self):
        po = self.participant.profile_object()
        assert len(po.keys()) == 3
        assert po.get('test2') == '3'
        assert po.get('test1_score') == 2.5
