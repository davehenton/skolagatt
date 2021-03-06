# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import current_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from common.models import Student
from samraemd.models import (
    SamraemdMathResult,
    SamraemdISLResult,
    SamraemdENSResult,
)

logger = get_task_logger(__name__)


@task(bind=True, name="save_samraemd_result", base=AbortableTask)
def save_samraemd_result(self, newdata):
    # Iterate through the data
    logger.info("Importing a new set of Samraemd results ({} entries)".format(len(newdata)))
    updated = 0
    added = 0
    newdata_len = len(newdata)
    loop_counter = 0
    for newentry in newdata:
        if self.is_aborted():
            logger.info("Aborted. Added {} entries, updated {} before that".format(added, updated))
            return False
        logger.debug("looking up {}".format(newentry['ssn']))
        student = Student.objects.filter(ssn=newentry['ssn'])
        loop_counter += 1
        current_task.update_state(state='PROGRESS', meta={
            'current': loop_counter,
            'total': newdata_len,
            'exam_code': newentry['exam_code'],
        })
        if not student.exists():
            logger.debug("Not found: {}".format(newentry['ssn']))
            continue

        del(newentry['ssn'])
        newentry['student'] = student.first()

        exam_type = newentry['exam_type']
        del(newentry['exam_type'])

        if exam_type == 'STÆ':
            results = SamraemdMathResult.objects.filter(
                student=newentry['student'], exam_code=newentry['exam_code'])

            if results:
                results.update(**newentry)
                updated += 1
            else:
                results = SamraemdMathResult.objects.create(**newentry)
                added += 1
        elif exam_type == 'ENS':
            results = SamraemdENSResult.objects.filter(
                student=newentry['student'], exam_code=newentry['exam_code'])

            if results:
                results.update(**newentry)
                updated += 1
            else:
                results = SamraemdENSResult.objects.create(**newentry)
                added += 1
        elif exam_type == 'ÍSL':
            results = SamraemdISLResult.objects.filter(
                student=newentry['student'], exam_code=newentry['exam_code'])

            if results:
                results.update(**newentry)
                updated += 1
            else:
                results = SamraemdISLResult.objects.create(**newentry)
                added += 1
    logger.info("Done. Added {} entries, updated {} entries".format(added, updated))
