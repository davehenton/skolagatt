def aldursbil(kennitala):
    '''Takes kennitala, returns aldursbil (age level)'''
    # INPUT: kennitala/ssn. preferably a string like DDMMYYXXXX
    # where DD is date, MM month, YY year, rest we don't care about.
    # OUTPUT: aldursbil. "bil 1", "bil 2", "bil 3"
    # where bil 1 means was born in jan-may, 2 means apr-aug, 3 means sep-dec.
    if not is_kennitala_valid(kennitala):
        # we have an error
        return "villa"
    else:
        month = int(kennitala[2:4])
        third_of_year = int(max(0, month - 1) / 4)  # rounds down
        third_to_aldursbil = {0: 'bil 1', 1: 'bil 2', 2: 'bil 3'}
        return third_to_aldursbil[third_of_year]


def is_kennitala_valid(kennitala):
    '''Returns false if kennitala/ssn is unusable to get date of birth'''
    # Temporary function. We're gonna write something more elegant connecting
    # to Thjodskra's kennitalas
    if not kennitala.isdigit():
        return False
    else:
        if len(str(kennitala)) < 6:
            return False
        elif not kennitala[0:2].isdigit() or not kennitala[2:4].isdigit() or not kennitala[4:6].isdigit():
            return False
        elif 1 > int(kennitala[0:2]) or 31 < int(kennitala[0:2]) or 1 > int(kennitala[2:4]) or 12 < int(kennitala[2:4]):
            # could've imported dateutils.parser to check (but we're gonna use thjodskra to check)
            return False
        else:
            return True
