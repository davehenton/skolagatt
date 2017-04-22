# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist

from celery import current_task
from celery.decorators import task
from celery.utils.log import get_task_logger

from common.models import (
    Student,
    ExampleSurveyAnswer,
    ExampleSurveyQuestion,
    GroupSurvey,
)

from survey.models import Survey

logger = get_task_logger(__name__)


@task(name="save_example_survey_answers")
def save_example_survey_answers(newdata):
    """Add new entries to ExampleSurveyAnswer model asynchronously"""
    student_cache = {}
    quickcode_cache = {}
    # Iterate through the data
    logger.info("Importing a new set of ExampleSurveyAnswers ({} entries)".format(len(newdata)))
    added = 0
    newdata_len = len(newdata)
    loop_counter = 0
    for newentry in newdata:
        ssn = newentry['ssn']
        quickcode = newentry['quickcode']
        loop_counter += 1
        try:
            if ssn not in student_cache.keys():
                student_cache[ssn] = Student.objects.get(ssn=newentry['ssn'])
            student = student_cache[ssn]
            if quickcode not in quickcode_cache.keys():
                quickcode_cache[quickcode] = ExampleSurveyQuestion.objects.get(quickcode=newentry['quickcode'])
            question = quickcode_cache[quickcode]
        except ObjectDoesNotExist as e:
            logger.debug("Unable to add entry for ssn: {}, quickcode: {}: ".format(ssn, quickcode, e.__str__()))
            continue

        exam_code = None
        groupsurvey = None
        survey_cache = {}
        survey_identifier = newentry['survey_identifier']

        if survey_identifier:
            if survey_identifier not in survey_cache.keys():
                survey = Survey.objects.filter(identifier=survey_identifier).first()
                if survey:
                    groupsurvey = GroupSurvey.objects.filter(survey=survey, studentgroup=student.studentgroup).first()
                    survey_cache[survey_identifier] = groupsurvey
                else:
                    survey_cache[survey_identifier] = False

            if not survey_cache[survey_identifier]:
                exam_code = newentry['survey_identifier']
            else:
                groupsurvey = survey_cache[survey_identifier]
        current_task.update_state(state='PROGRESS', meta={
            'current': loop_counter,
            'total': newdata_len,
            'exam_code': exam_code,
        })
        added += 1
        boolanswer = True if newentry['answer'] == '1' else False
        ExampleSurveyAnswer.objects.create(
            student=student,
            question=question,
            groupsurvey=groupsurvey,
            exam_code=exam_code,
            date=newentry['exam_date'],
            answer=boolanswer,
        )

    logger.info("Done. Added {} entries".format(added))
    return
