import sys
import time
import math
from queue import Queue
import threading

import numpy as np
import pandas as pd
from pandas_gbq import read_gbq

from helpers import parse_arguments
from google.oauth2 import service_account

from visualize_bokeh import generate_bokeh_dashboard
import deploymodel as dm
MAX_BATCH_SIZE = 60
columns = 'TIMESTAMP,ROLL,PITCH,ALTITUDE,VELOCITY_2D,VELOCITY_3D,THROTTLE,BATTERY_mAh,qnh,ASML_BARO,TAS,D_ROLL,D_PITCH,D_ALTITUDE,FAULT'.split(',')


def restream_dataframe(dataframe, bokeh_port=5006):
    # 4. launch dashboard
    # Queue to communicate between restreamer and dashboard threads
    update_queue = Queue()
    if int(bokeh_port):
        generate_bokeh_dashboard(
            columns,
            title="Drone Fault Detection", cols=3, port=int(bokeh_port), update_queue=update_queue
        )

    restream_thread = threading.Thread(
        target=threaded_restream_dataframe,
        args=(dataframe, bokeh_port, update_queue)
    )
    restream_thread.start()


def threaded_restream_dataframe(dataframe, bokeh_port, update_queue, interval=3, sleep_interval=1):
    batches = np.array_split(dataframe, math.ceil(dataframe.shape[0] / MAX_BATCH_SIZE))
    model = dm.model

    first_pass = True
    for idx in range(len(batches)):
        end_time = np.min(batches[idx]['TIMESTAMP'])
        recreate_index = first_pass

        while end_time < np.max(batches[idx]['TIMESTAMP']):
            end_time += interval*1000
            batch_for_fault_detection = batches[idx][['Ax','Ay','Az','Gx','Gy','Gz','C1','C2']]  # fault 감지용
            dataframe.loc[idx*MAX_BATCH_SIZE:(idx+1)*MAX_BATCH_SIZE, 'FAULT'] = pd.Series(model.predict(batch_for_fault_detection.to_numpy()))
            if not recreate_index:
                while np.round(time.time()) < end_time/1000.:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    time.sleep(sleep_interval)

            if bokeh_port:
                update_queue.put(batches[idx][columns])
            recreate_index = False
        first_pass = False


def main():
    args = parse_arguments()
    # 1. load data
    print('Loading the data...')
    credentials = service_account.Credentials.from_service_account_file('FILE_LOCATION/YOUR_JSON_FILE_NAME.json')
    dataframe = read_gbq(
        project_id='YOUR_PROJECT_ID',
        credentials=credentials,
        dialect='standard',
        query='select * from BIGQUERY_TABLE_NAME'
    )
    dataframe['FAULT'] = pd.Series(np.zeros(len(dataframe)))
    del dataframe['EVENT_DATA']
    print('Done.\n')


    # 2. make timefield
    start = int(time.time())
    dataframe['TIMESTAMP'] = pd.Series(range(start, start+dataframe.shape[0]))
    now = np.round(time.time() * 1000)
    first_timestamp = dataframe['TIMESTAMP'][0]
    dataframe['TIMESTAMP'] = now + (dataframe['TIMESTAMP'] -first_timestamp).astype('float') / float(args.speed)

    restream_dataframe(dataframe=dataframe, bokeh_port=int(args.bokeh_port))


if __name__ == '__main__':
    main()