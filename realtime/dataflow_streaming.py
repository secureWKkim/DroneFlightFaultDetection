#!/usr/bin/env python3

import apache_beam as beam

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def create_row(fields):
    header = 'TIMESTAMP,ROLL,PITCH,ALTITUDE,VELOCITY_2D,VELOCITY_3D,Fault_Telemetry,THROTTLE,BATTERY_mAh,qnh,ASML_BARO,TAS,D_ROLL,D_PITCH,D_ALTITUDE'.split(',')
    featdict = {}
    for name, value in zip(header, fields):
        featdict[name] = value
    return featdict


def run(project, bucket, region):
    argv = [
        '--project={0}'.format(project),
        '--job_name=tryavgdelaywithcreaterow',
        '--streaming',
        '--save_main_session',
        '--staging_location=gs://{0}/flights/staging/'.format(bucket),
        '--temp_location=gs://{0}/flights/temp/'.format(bucket),
        '--autoscaling_algorithm=THROUGHPUT_BASED',
        '--max_num_workers=8',
        '--region={}'.format(region),
        '--runner=DataflowRunner'
    ]

    with beam.Pipeline(argv=argv) as pipeline:
        events = {}

        for event_name in ['dashboard']:  # 나중에 리스트에 원소 더 추가될수도 있으니 수정 ㄴㄴ
            topic_name = "projects/{}/topics/{}".format(project, event_name)

            events[event_name] = (pipeline
                                  | 'read:{}'.format(event_name) >> beam.io.ReadFromPubSub(
                                                topic=topic_name, timestamp_attribute='TIMESTAMP')
                                  )

        stats_schema = 'TIMESTAMP:timestamp,ROLL:float,PITCH:float,ALTITUDE:float,VELOCITY_2D:float,VELOCITY_3D:float,Fault_Telemetry:integer,THROTTLE:float,BATTERY_mAh:float,qnh:float,ASML_BARO:float,TAS:float,D_ROLL:float,D_PITCH:float,D_ALTITUDE:float,EVENT_DATA:string'
        (events[event_name]
         | 'createrow' >> beam.Map(lambda fields: create_row(fields))
         | 'bqout' >> beam.io.WriteToBigQuery(
                    'for_dashboard_data.streaming_delays', schema=stats_schema,
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                )
         )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run pipeline on the cloud')
    parser.add_argument('-p', '--project', help='Unique project ID', required=True)
    parser.add_argument('-b', '--bucket', help='Bucket where gs://BUCKET/flights/airports/airports.csv.gz exists',
                        required=True)
    parser.add_argument('-r', '--region',
                        help='Region in which to run the Dataflow job. Choose the same region as your bucket.',
                        required=True)

    args = vars(parser.parse_args())

    run(project=args['project'], bucket=args['bucket'], region=args['region'])