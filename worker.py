import datetime
import functools
import threading
import pika
from pika.exceptions import ChannelClosedByBroker
from pika.exchange_type import ExchangeType

from api import ServiceApi
from parser import AppParser


def ack_message(ch, delivery_tag):
    """Note that `ch` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if ch.is_open:
        ch.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass

def do_work(ch, delivery_tag, body):
    thread_id = threading.get_ident()
    print('Thread id: %s Delivery tag: %s Message body: %s date: %s', thread_id,
                delivery_tag, body,str(datetime.datetime.now()))
    package = body.decode()
    app = ServiceApi.get_app_by_package(package).json()
    if app:
        parser = AppParser(package)
        app_info = parser.check()
        if app_info['status'] == 0:
            history_record = {'app_id':app['id'],'category':app['category'],'count_downloads':app_info['count']}
            if app['status'] == 'IN_DEVELOPING':
                history_record['status'] = 'PUBLISHED'
                app['status'] = 'PUBLISHED'
            res = ServiceApi.save_scan(history_record)
            app['count_downloads'] = app_info['count']
            ServiceApi.update_app_info(app['id'], app)
        elif app_info['status'] == 1:
            if app['status'] == 'IN_DEVELOPING':
                history_record = {'app_id': app['id'], 'category': app['category'],
                                  'count_downloads': 0,'status':'IN_DEVELOPING'}
                res = ServiceApi.save_scan(history_record)
            elif app['status'] == 'PUBLISHED' or app['status'] == 'SALES':
                history_bloked = ServiceApi.get_blocked(app['id'])
                if len(history_bloked) >= 2:
                    app['status'] = 'BLOCKED'
                    ServiceApi.update_app_info(app['id'], app)
                history_record = {'app_id': app['id'], 'category': app['category'],
                                  'count_downloads': app_info['count'],'status':'BLOCKED'}
                res = ServiceApi.save_scan(history_record)
    else:
        print('Not found package in db')
    cb = functools.partial(ack_message, ch, delivery_tag)
    ch.connection.add_callback_threadsafe(cb)

def on_message(ch, method_frame, _header_frame, body, args):
    thrds = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(ch, delivery_tag, body))
    t.start()
    thrds.append(t)

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(connection_attempts=1,
        host='192.248.191.78', credentials=credentials, heartbeat=100))
channel = connection.channel()
channel.exchange_declare(
    exchange="app_exchange",
    exchange_type=ExchangeType.direct,
    passive=False,
    durable=True,
    auto_delete=False)
channel.queue_declare(queue='app_queue', durable=True)
channel.queue_bind(
    queue="app_queue", exchange="app_exchange", routing_key="standard_key")
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.basic_qos(prefetch_count=1)

threads = []
on_message_callback = functools.partial(on_message, args=(threads))
channel.basic_consume(on_message_callback=on_message_callback,queue='app_queue')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except ChannelClosedByBroker:
    print('ChannelClosedByBroker date',str(datetime.datetime.now()))

# Wait for all to complete
for thread in threads:
    thread.join()

connection.close()