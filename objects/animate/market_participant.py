import json
import abc
from abc import ABC, abstractmethod
import pika


class MarketParticipant(ABC):
    # @abc.abstractproperty
    # def id(self):
    #     pass

    def place_buy_limit_order(self, ticker, market, price):
        RABBIT_MQ_HOST = "localhost"
        QUEUE_NAME = "orders_to_process"

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)

        params = {
            "type": "buy",
            "price": price,
            "offeror_id": self.id,
            "ticker": ticker,
        }

        channel.basic_publish(
            exchange="", routing_key=QUEUE_NAME, body=json.dumps(params)
        )

        # print("Just added a buy order to the queue")
        connection.close()

        # market.process_bid(price, self, ticker)
        # self.save()

    def place_sell_limit_order(self, share, market, price):
        RABBIT_MQ_HOST = "localhost"
        QUEUE_NAME = "orders_to_process"

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)

        params = {
            "type": "sell",
            "price": price,
            "offeror_id": self.id,
            "share_id": share.id,
        }

        channel.basic_publish(
            exchange="", routing_key=QUEUE_NAME, body=json.dumps(params)
        )

        # print("Just added a sell order to the queue")
        connection.close()

        # market.process_ask(price, self, share)
        # self.save()

    # @abstractmethod
    # def place_buy_market_order(price):
    #     pass

    # @abstractmethod
    # def place_sell_market_order(price):
    #     pass
