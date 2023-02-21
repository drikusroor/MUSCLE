from copy import deepcopy
import random

from .profile_scoring_rules import PROFILE_SCORING_RULES
from .demographics import DEMOGRAPHICS

from result.utils import prepare_result
from result.models import Result

def total_unanswered_questions(participant, questions=DEMOGRAPHICS):
    """ Return how many questions have not been answered yet by the participant"""
    profile_questions = participant.profile().exclude(
        given_response=None
    ).values_list('question_key', flat=True)
    return len([question for question in questions if question.key not in profile_questions])

def question_by_key(key, questions=DEMOGRAPHICS, is_skippable=None, drop_choices=[]):
    """Return question by given key"""
    for question in questions:
        if question.key == key:
            q = deepcopy(question)
            # Question is_skippable
            if is_skippable != None:
                q.is_skippable = is_skippable
            if hasattr(question, 'choices') and len(drop_choices):
                for choice in drop_choices:
                    q.choices.pop(choice, None)
            return q
    return None

def unasked_question(participant, questions=DEMOGRAPHICS, randomize=False):
    """Get unasked question and prepare its result
    - session: session whose participant will be checked for unanswerd questions
    - questions: list of questions from which to select an unanswered question
    - optionally, randomize order of questions
    """
    if randomize:
        random.shuffle(questions)
    profile_questions = participant.profile_questions()
    for question in questions:
        if not question.key in profile_questions:
            q = deepcopy(question)
            try:
                result_id = participant.profile().get(question_key=q.key)
            except Result.DoesNotExist:
                result_id = prepare_result(
                    question.key,
                    participant=participant,
                    scoring_rule=PROFILE_SCORING_RULES.get(question.key, '')
                )
            q.result_id = result_id
            return q
    return None