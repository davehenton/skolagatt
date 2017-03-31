from celery.decorators import task
from celery.utils.log import get_task_logger

from common.models import (
	Student,
	ExampleSurveyAnswer,
	ExampleSurveyQuestion,
)

logger = get_task_logger(__name__)


@task(name="save_example_survey_answers")
def save_example_survey_answers(newdata):
    """Add new entries to ExampleSurveyAnswer model asynchronously"""
    student_cache = {}
    quickcode_cache = {}
    # Iterate through the data
    logger.info("Importing a new set of ExampleSurveyAnswers ({} entries)".format(len(newdata)))
    updated = 0
    added = 0

    for newentry in newdata:
        ssn = newentry['ssn']
        quickcode = newentry['quickcode']
        try:
            if not ssn in student_cache.keys():
                student_cache[ssn] = Student.objects.get(ssn=newentry['ssn'])
            student = student_cache[ssn]
            if not quickcode in quickcode_cache.keys():
                quickcode_cache[quickcode] = ExampleSurveyQuestion.objects.get(quickcode = newentry['quickcode'])
            question = quickcode_cache[quickcode]
        except:
            logger.debug("Unable to add entry for ssn: {}, quickcode: {}".format(ssn, quickcode))
            continue

        exam_code = None
        groupsurvey = None
        survey_cache = {}
        survey_identifier = newentry['survey_identifier']

        if survey_identifier:
            if not survey_identifier in survey_cache.keys():
                survey = Survey.objects.filter(identifier = survey_identifier).first()
                if survey:
                    groupsurvey = GroupSurvey.objects.filter(survey = survey, studentgroup = studentgroup).first()
                    survey_cache[survey_identifier] = groupsurvey
                else:
                    survey_cache[survey_identifier] = False

            if not survey_cache[survey_identifier]:
                exam_code = newentry['survey_identifier']
            else:
                groupsurvey = survey_cache[survey_identifier]

        answer = ExampleSurveyAnswer.objects.filter(
            student = student,
            question = question,
            date = newentry['exam_date'],
        )

        boolanswer = True if newentry['answer'] == '1' else False

        if answer:
            updated += 1
            answer.update(
                groupsurvey = groupsurvey,
                exam_code = exam_code,
                answer = boolanswer,
            )
        else:
            added += 1
            answer = ExampleSurveyAnswer.objects.create(
                student = student,
                question = question,
                groupsurvey = groupsurvey,
                exam_code = exam_code,
                date = newentry['exam_date'],
                answer = boolanswer,
            )
    logger.info("Done. Added {} entries, updated {} entries".format(added, updated))
    return
