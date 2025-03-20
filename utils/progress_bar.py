import math

def level_cap(experience):
    '''
    the total experience points required to reach the next level
    '''
    return level_to_experience(experience_to_level(experience)+1)

def level_bottom(experience):
    '''
    the total experience points required to reach the current level
    '''
    return level_to_experience(experience_to_level(experience))
    
def experience_to_level(value):
    '''
    convert experience to level
    '''
    return math.floor(math.sqrt(value / 6 + 0.25) + 0.5)

def level_to_experience(level):
    '''
    convert level to the minimum experience required to reach that level
    '''
    return 6 * level * (level - 1)

def generate_bar(experience, progress_bar_length):
    '''
    generate an text progress bar with custom length using ascii symbol.
    '''
    experience_earned_since_current_level = experience - level_bottom(experience)
    experience_required_to_level_up = level_cap(experience) - level_bottom(experience)
    length = round(experience_earned_since_current_level / experience_required_to_level_up * progress_bar_length)
    return '▰' * length + '▱' * (progress_bar_length - length)

def generate_custom_bar(current_exp, exp_needed):
    '''
    directly generate the ascii progress bar from given values.
    used for the habitica progress bar in taskwarrior
    '''
    progress_bar_length = 24
    length = round(current_exp / exp_needed * progress_bar_length)
    return '▰' * length + '▱' * (progress_bar_length - length)

def generate_statistics_row(key, value, is_show_level = True):
    '''
    generate progress bar from dictionary
    used in the skill section of the blog
    '''
    level = experience_to_level(value)
    progress_bar_length = 24
    if is_show_level:
        if value == -1:
            statistics_row = (key.capitalize() + ': ').rjust(30, ' ') + '0'.rjust(3) + ' --- ' + 'Lv0\n\n'
        else:
            statistics_row = (key.capitalize() + ': ').rjust(30, ' ') + str(value).rjust(3) + ' --- ' + 'Lv' + str(level) + ' '+ generate_bar(value, progress_bar_length) + '\n\n'
    else:
        statistics_row = (key.capitalize() + ': ').rjust(30, ' ') + str(value).rjust(3) + '\n\n'
    return statistics_row
