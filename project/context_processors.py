def menu(request):
    menu = ['Phone','Data','Voice']
    return {
        'menu_list': menu
    }