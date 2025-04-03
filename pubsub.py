
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

class AsyncConn:
    def __init__(self, id: str, channel_name: str) -> None:
        config = PNConfiguration()
        config.subscribe_key = 'sub-c-94e80db1-0feb-445b-8713-96743f49b7ba'
        config.publish_key = 'pub-c-3f89551e-108a-40d0-b357-a7cd07520272'
        config.user_id = id
        config.enable_subscribe = True
        config.daemon = True

        self.pubnub = PubNub(config)
        self.channel_name = channel_name

        print(f"Configurando conexão com o canal '{self.channel_name}'...")
        subscription = self.pubnub.channel(self.channel_name).subscription()
        subscription.subscribe()

    def publish(self, data: dict):
        print("tentando enviar uma mensagem")
        self.pubnub.publish().channel(self.channel_name).message(data).sync()

