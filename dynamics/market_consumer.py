import json
from threading import Thread
import objects.animate.market  # Do not import class because of circular dependency
from db_interface.dao_MongoDB import Dao
import pika

RABBIT_MQ_HOST = "localhost"
QUEUE_NAME = "orders_to_process"


class MarketConsumer(Thread):
    def __init__(self, market_id):

        self.market_id = market_id

        Thread.__init__(self)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ_HOST)
        )
        self.channel = connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, auto_delete=False)
        # self.channel.basic_qos(prefetch_count=THREADS*10)
        self.channel.basic_consume(
            QUEUE_NAME, on_message_callback=self.callback, auto_ack=True
        )

        Thread(
            target=self.channel.basic_consume(
                QUEUE_NAME, on_message_callback=self.callback
            )
        )

    def callback(self, channel, method, properties, body):
        params = json.loads(body)
        dao = Dao()
        market = dao.find_objects(objects.animate.market.Market, [self.market_id])[
            self.market_id
        ]

        if params["type"] == "buy":
            market.process_bid(params["price"], params["offeror_id"], params["ticker"])
        elif params["type"] == "sell":
            market.process_ask(
                params["price"], params["offeror_id"], params["share_id"]
            )

    def run(self):
        print("starting thread to consume from rabbit...")
        self.channel.start_consuming()
