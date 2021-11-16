import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bokeh-port", help="Bokeh server port", default="5006")
    return parser.parse_args()