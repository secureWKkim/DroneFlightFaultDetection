from pandas import read_gbq
import os
from helpers import parse_arguments
from queue import Queue
from visualize_bokeh import generate_bokeh_dashboard
from pandas_gbq import read_gbq
from google.oauth2 import service_account


def main():
    args = parse_arguments()
    # 1. load data
    print('Loading the data...')
    credentials = service_account.Credentials.from_service_account_file('/Users/wonkyungkim/Documents/GitHub/google-cloud-platform/04_streaming/simulate/silver-seat-328814-0c280dde0bc1.json')
    dataframe = read_gbq(
        project_id='silver-seat-328814',
        # credentials=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
        credentials=credentials,
        dialect='standard',  # 얜 뭐꼬
        query='select * from for_dashboard_data.streaming_delays'  # silver-seat-328814
    )
    print('Done.\n')


    # 2. make timefield
    # dataframe[timefield] = (now + (dataframe[timefield] -
    #                                    first_timestamp)/speed).astype(int)
    # 위와 같은 과정이 들어감, 근데이걸로 뭘 어쨰하는지 몰겠으니 코드 읽어보고 넣을지 결정. timestamp 값 그대로 쓰는 customize 방안도 있으니...


    # 3. select fields
    # fields = dataframe.columns

    # 4. launch dashboard
    # Queue to communicate between restreamer and dashboard threads
    update_queue = Queue()
    if int(args.bokeh_port):
        generate_bokeh_dashboard(
            dataframe.columns, title="Drone Fault Detection", cols=3,
            port=int(args.bokeh_port), update_queue=update_queue
        )

if __name__ == '__main__':
    main()