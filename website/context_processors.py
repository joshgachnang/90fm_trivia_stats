from website.models import during_trivia, get_last_hour, get_last_year, get_start_time


def default_template_variables(request):
    template_data = {}
    template_data['last_year'] = get_last_year()
    template_data['last_hour'] = get_last_hour()
    template_data['during_trivia'] = during_trivia()
    template_data['trivia_start_time'] = get_start_time()
    return template_data

