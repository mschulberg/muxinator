#!/usr/bin/env python
import yaml
import logging
import logging.handlers



class Config():
    def __init__(self, **kwargs):
        for k,v in kwargs['default'].items():
            setattr(self, k, v)
    def __repr__(self):
        return self.__dict__.__str__()
    def get(self, key, default):
        return self.__dict__.get(key, default)

with open('config.yml') as f:
    config = Config(**yaml.full_load(f))

def build_logger(logname=__name__):
    logger = logging.getLogger(logname)
    logger.setLevel(config.get('loglevel', 'DEBUG'))
    file_handler = logging.FileHandler(config.get('logfile', 'log.tmuxify'))
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

