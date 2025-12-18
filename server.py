import asyncio
import json
import logging

import tornado.web
import tornado.websocket
import aiomqtt

broker = "test.mosquitto.org"
topic_temperature = "sensor/temperature"
topic_humidity = "sensor/humidity"
topic_pressure = "sensor/pressure"

clients = set()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket aperto")
        clients.add(self)

    def on_close(self):
        print("WebSocket chiuso")
        clients.remove(self)


async def mqtt_listener():

    logging.info("Connessione al broker MQTT...")

    async with aiomqtt.Client(broker) as client:
        await client.subscribe(topic_temperature)
        logging.info(f"Iscritto al topic: {topic_temperature}")

        async for message in client.messages:
            payload = message.payload.decode()
            data = json.loads(payload)

            ws_message = json.dumps({
                "type": "sensor",
                "data": data
            })

            # inoltro ai client WebSocket
            for c in list(clients):
                await c.write_message(ws_message)



async def main():
    logging.basicConfig(level=logging.INFO)

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/ws", WSHandler),
        ],
        template_path="templates",
    )

    app.listen(8888)
    print("Server Tornado avviato su http://localhost:8888")

    asyncio.create_task(mqtt_listener())

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
