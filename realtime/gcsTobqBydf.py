import apache_beam as beam
import csv
import datetime

def create_row(fields):
    header = 'TIMESTAMP,ROLL,PITCH,ALTITUDE,VELOCITY_2D,VELOCITY_3D,THROTTLE,BATTERY_mAh,qnh,ASML_BARO,TAS,D_ROLL,D_PITCH,D_ALTITUDE'.split(',')
    featdict = {}
    for name, value in zip(header, fields):
        featdict[name] = value
    featdict['EVENT_DATA'] = ','.join(fields)
    return featdict


def run(project, bucket, dataset, region):
    argv = [
        '--project={0}'.format(project),
        '--job_name=gcstodftobq',
        '--save_main_session',
        '--staging_location=gs://{0}/staging/'.format(bucket),  # 없으면 에러남
        '--temp_location=gs://{0}/temp/'.format(bucket),  # 없으면 에러남
        '--setup_file=./setup.py',
        '--max_num_workers=8',
        '--region={}'.format(region),
        '--autoscaling_algorithm=THROUGHPUT_BASED',
        '--runner=DataflowRunner'
    ]
    main_filename = 'gs://{}/binary_gcs_file.csv'.format(bucket)
    dashboard_output_forgcs = 'gs://{}/output/dashboard_output_timestampver'.format(bucket)
    dashboard_output = '{}:{}.fordashboard'.format(project, dataset)

    pipeline = beam.Pipeline(argv=argv)

    dashboards = (pipeline
                | 'dashboards:read' >> beam.io.ReadFromText(main_filename)
                | 'dashboards:fields' >> beam.Map(lambda line: next(csv.reader([line])))
                | 'dashboards:select' >> beam.Map(lambda fields: (
            str(datetime.datetime.now()), fields[1], fields[2], fields[11], fields[12],
            fields[14], fields[25], fields[29], fields[34], fields[35], fields[37], fields[38], fields[39],
            fields[43])))

    (dashboards
     | 'dashboard:tostring' >> beam.Map(lambda fields: ','.join(fields))
     | 'dashboard:out' >> beam.io.textio.WriteToText(dashboard_output_forgcs)
     )

    dashboard_schema = 'TIMESTAMP:timestamp,ROLL:float,PITCH:float,ALTITUDE:float,VELOCITY_2D:float,VELOCITY_3D:float,THROTTLE:float,BATTERY_mAh:float,qnh:float,ASML_BARO:float,TAS:float,D_ROLL:float,D_PITCH:float,D_ALTITUDE:float,EVENT_DATA:string'
    (dashboards
     | 'dashboardevents:totablerow' >> beam.Map(lambda fields: create_row(fields))
     | 'dashboardevents:out' >> beam.io.WriteToBigQuery(
                dashboard_output, schema=dashboard_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED)
     )

    pipeline.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run pipeline on the cloud')
    parser.add_argument('-p', '--project', help='Unique project ID', required=True)
    parser.add_argument('-b', '--bucket', help='Bucket where your data were ingested in Chapter 2', required=True)
    parser.add_argument('-r', '--region',
                        help='Region in which to run the Dataflow job. Choose the same region as your bucket.',
                        required=True)
    parser.add_argument('-d', '--dataset', help='BigQuery dataset', default='for_dashboard_data')
    args = vars(parser.parse_args())

    print("Correcting timestamps and writing to BigQuery dataset {}".format(args['dataset']))

    run(project=args['project'], bucket=args['bucket'], dataset=args['dataset'], region=args['region'])
