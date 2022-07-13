import logging
from .views import Final

logger = logging.getLogger(__name__)

class Base(object):
    """Base class for other rules classes"""

    @classmethod
    def prepare_result(cls, session, section, expected_response=None):
        # Prevent circular dependency errors
        from experiment.models import Result

        result = Result(session=session)
        result.section = section
        if expected_response is not None:
            result.expected_response = expected_response
        result.save()
        return result.pk
    
    @staticmethod
    def save_result(result_data):    
        from experiment.models import Result
        # TODO: WARNING: make sure that the requested session is part of the current session
        result = Result.objects.get(pk=result_data['result_id'])
        result.given_response = result_data['value']
        result.save()
        return result.expected_response

    
    @staticmethod
    def handle_results(session, data):
        """ 
        if the given_result is an array of results, retrieve and save results for all of them
        to use, override hande_result and call this method
        """

        from experiment.models import Result
        # TODO: WARNING the following line removes all form data from the stored result; 
        # this way information about the given answer is lost
        form = data.pop('form') 
        for form_element in form:
            try:
                result = Result.objects.get(pk=form_element['result_id'], session=session)
            except Result.DoesNotExist:
                # Create new result
                result = Result(session=session)
            # Calculate score
            score = session.experiment_rules().calculate_score(result, form_element, data)
            if not score:
                score = 0
            result.given_response = form_element['value']
            result.save_json_data(data)
            result.score = score
            result.save()
        return result

    @staticmethod
    def handle_result(session, data):
        """Create a result for given session, based on the result data and section_id"""
        from experiment.models import Result
        
        # Get existing result or create a new
        if "result_id" in data:
            try:
                result = Result.objects.get(pk=data['result_id'], session=session)
            except Result.DoesNotExist:
                result = Result(session=session)
        else:
            result = Result(session=session)

        # Calculate score
        score = session.experiment_rules().calculate_score(session, None, data)
        if not score:
            score = 0


        # Populate and save the result
        result.save_json_data(data)
        result.score = score
        result.save()

        return result

    @staticmethod
    def calculate_score(result, form_element, data):
        """fallback for calculate score"""
        return None

    @staticmethod
    def final_score_message(session):
        """Create final score message for given session, base on score per result"""

        correct = 0
        total = 0

        for result in session.result_set.all():
            # if a result has score != 0, it was recognized
            if result.score:
                total += 1

                if result.score > 0:
                    # if a result has score > 0, it was identified correctly
                    correct += 1

        score_message = "Well done!" if session.final_score > 0 else "Too bad!"
        message = "You correctly identified {} out of {} recognized songs!".format(
            correct,
            total
        )
        return score_message + " " + message

    @staticmethod
    def rank(session):
        """Get rank based on session score"""
        score = session.final_score
        ranks = Final.RANKS

        # Few or negative points or no score, always return lowest plastic score
        if score <= 0 or not score:
            return ranks['PLASTIC']

        # Buckets for positive scores:
        # rank: starts percentage
        buckets = [
            # ~ stanines 1-3
            {'rank': ranks['BRONZE'],   'min_percentile':   0.0},
            # ~ stanines 4-6
            {'rank': ranks['SILVER'],   'min_percentile':  25.0},
            # ~ stanine 7
            {'rank': ranks['GOLD'],     'min_percentile':  75.0},
            {'rank': ranks['PLATINUM'],
                'min_percentile':  90.0},   # ~ stanine 8
            {'rank': ranks['DIAMOND'],
                'min_percentile':  95.0},   # ~ stanine 9
        ]

        percentile = session.percentile_rank()

        # Check the buckets in reverse order
        # If the percentile rank is higher than the min_percentile
        # return the rank
        for bucket in reversed(buckets):
            if percentile >= bucket['min_percentile']:
                return bucket['rank']

        # Default return, in case score isn't in the buckets
        return ranks['PLASTIC']
