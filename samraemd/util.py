from common.models import StudentGroup


def get_results_from_sheet(sheet, row, result_length):
    """
    Grabs results from sheet when importing raw data from Excel documents
    Arguments:
        sheet        : sheet to grab from
        row          : current row
        result_length: length of results
    """
    result_data = {}
    try:
        # Loop through entire row
        for numb in range(0, int(result_length)):
            # n is the current iterator converted to a string and with 0 prepended if < 10
            n = str(numb) if numb >= 10 else "0" + str(numb)
            result_data[n] = {
                'id': str(sheet.cell_value(0, numb + 1)).strip(),  # Question id
                'category': str(sheet.cell_value(1, numb + 1)).strip(),  # Question category
                'context': str(sheet.cell_value(2, numb + 1)).strip(),  # Context of question
                'description': str(sheet.cell_value(3, numb + 1)).strip(),  # Question description
                'img': str(sheet.cell_value(4, numb + 1)).strip(),
                'value': int(sheet.cell_value(row, numb + 1))  # Student's answer to question
            }
    except Exception as e:
        print(e)

    return result_data


def display_raw_results(results, student_results, student_group, col_names):
    for result in results:
        if result.student in student_results:
            student_results[result.student].append(result)
            if StudentGroup.objects.filter(
                students=result.student
            ) in student_group[result.student]:
                student_group[result.student].append(
                    StudentGroup.objects.filter(students=result.student)
                )
        else:
            student_results[result.student] = [result]
            student_group[result.student] = StudentGroup.objects.filter(students=result.student)
        if result.exam_code not in col_names:
            col_names[result.exam_code] = result
