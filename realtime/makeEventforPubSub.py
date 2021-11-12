import logging
import argparse
from google.cloud import pubsub
import google.cloud.bigquery as bq


def publish(publisher, topics, allevents):
    for key in topics:
        topic = topics[key]
        events = allevents[key]
        for event_data in events:
            publisher.publish(topic, event_data['EVENT_DATA'].encode())  # EventTimeStamp=timestamp


def notify(publisher, topics, rows):
    tonotify = {}
    for key in topics:
        tonotify[key] = list()

    for row in rows:
        event_data = row
        tonotify['dashboard'].append(event_data)

    publish(publisher, topics, tonotify)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send simulated flight events to Cloud Pub/Sub')
    parser.add_argument('--project', help='your project id, to create pubsub topic', default='silver-seat-328814')

    # set up BigQuery bqclient
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)  # 이건 뭐하는건지 몰
    args = parser.parse_args()
    bqclient = bq.Client(args.project)
    dataset = bqclient.get_dataset(bqclient.dataset('for_dashboard_data'))  # throws exception on failure

    querystr = """
    SELECT EVENT_DATA
    FROM
      for_dashboard_data.fordashboard
    ORDER BY
      TIMESTAMP ASC
    """
    rows = bqclient.query(querystr)

    publisher = pubsub.PublisherClient()
    topics = {}
    topics['dashboard'] = publisher.topic_path(args.project, 'dashboard')
    try:
        publisher.get_topic(topics['dashboard'])
    except:
        publisher.create_topic(topics['dashboard'])

    notify(publisher, topics, rows)
