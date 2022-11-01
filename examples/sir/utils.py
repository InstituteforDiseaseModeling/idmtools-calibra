import os

from idmtools.entities import CommandLine

CALCULON = 'CALCULON'
LOCAL = 'LOCAL'


def generate_command(locale, model_driver, sif_filename, config_file):
    # generates an executable command for the model driver given specified info for arguments
    if locale == CALCULON:
        command = CommandLine("singularity exec ./Assets/%s python3 Assets/%s --config %s" %
                              (sif_filename,
                               os.path.basename(model_driver),
                               config_file)
                              )
    elif locale == LOCAL:
        raise Exception('local running via this method not currently implemented')
        command = CommandLine("singularity exec ./Assets/%s python3 Assets/%s --config %s" %
                              (sif_filename,
                               os.path.basename(model_driver),
                               config_file)
                              )
    else:
        raise Exception('Unknown locale: %s' % locale)
    return command

