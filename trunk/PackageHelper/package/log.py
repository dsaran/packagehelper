import logging

def set_log_file(filename, mask=None):
    """
    @param filename:
    @param mask: optional
    """
    file_handler = logging.FileHandler(filename, 'w')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(name)-18s %(levelname)-8s %(message)s',
        datefmt='%F %T'))
    root = logging.getLogger()
    root.addHandler(file_handler)

#    if mask:
#        file_filter = ReversedGlobalFilter()
#        file_filter.add_filter(mask, logging.DEBUG)
#        file_handler.addFilter(file_filter)

    return file_handler.stream

