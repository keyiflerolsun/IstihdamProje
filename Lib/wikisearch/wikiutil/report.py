def stringify_main_options(options):
    main_options = ''
    for index, option in enumerate(options.keys()):
        main_options += f'{index + 1}. {option}\n'
    return main_options

def stringify_sub_options(options, main_option):
    sub_options = ''
    if main_option not in options.keys():
        return None

    for index, sub_option in enumerate(options[main_option]):
        sub_options += f'{index + 1}. {sub_option.name}\n'
    return sub_options
    
    

    