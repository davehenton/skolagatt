def aldursbil(kennitala):
    '''Takes kennitala, returns aldursbil (age level)'''
    # INPUT: kennitala/ssn. preferably a string like DDMMYYXXXX
    # where DD is date, MM month, YY year, rest we don't care about.
    # OUTPUT: aldursbil. "bil 1", "bil 2", "bil 3"
    # where bil 1 means was born in jan-may, 2 means apr-aug, 3 means sep-dec.

    month = int(kennitala[2:4])
    third_of_year = int(max(0, month - 1)/ 4)  # rounds down
    third_to_aldursbil = {0: 'bil 1', 1: 'bil 2', 2: 'bil 3'}
    return third_to_aldursbil[third_of_year]