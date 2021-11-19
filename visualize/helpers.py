import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bokeh-port", help="Bokeh server port", default="5006")
    parser.add_argument("--speed", help="Restreamer speed", default="1.0")
    return parser.parse_args()