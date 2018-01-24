import stripe
import json

from nio import GeneratorBlock
from nio.signal.base import Signal
from nio.properties import VersionProperty, StringProperty, IntProperty, \
    PropertyHolder, ObjectProperty
from nio.modules.web import RESTHandler, WebEngine


class BuildSignal(RESTHandler):

    def __init__(self, endpoint, notify_signals, logger, webhook_secret):
        super().__init__('/'+endpoint)
        self.notify_signals = notify_signals
        self.logger = logger
        self.webhook_secret = webhook_secret

    def before_handler(self, req, rsp):
        # Overridden in order to skip the authentication in the framework
        return

    def on_post(self, req, rsp):
        body = req._body.read(req._get_length()).decode('utf-8')
        received_sig = req.get_header('Stripe-Signature', None)

        try:
            event = stripe.Webhook.construct_event(
                body, received_sig, self.webhook_secret)
        except ValueError:
            print("Error while decoding event!")
            return 'Bad payload', 400
        except stripe.error.SignatureVerificationError:
            print("Invalid signature!")
            return 'Bad signature', 400

        self.logger.debug("Received event: id={id}, type={type}".format(
            id=event.id, type=event.type))

        payload = json.loads(body)

        if not isinstance(payload, dict):
            self.logger.error("Invalid JSON in body: {}".format(payload))
            return

        self.notify_signals([Signal(payload)])


class WebServer(PropertyHolder):

    host = StringProperty(title='Host', default='0.0.0.0')
    port = IntProperty(title='Port', default=8182)
    endpoint = StringProperty(title='Endpoint', default='')


class Stripe(GeneratorBlock):

    version = VersionProperty("0.1.1")
    web_server = ObjectProperty(
        WebServer, title='Web Server', default=WebServer())
    webhook_secret = StringProperty(
        title="Stripe webhook secret key", default="[[STRIPE_WEBHOOK_SECRET]]")

    def __init__(self):
        super().__init__()
        self._server = None
        self._subscription_id = None

    def configure(self, context):
        super().configure(context)
        self._create_web_server()

    def start(self):
        super().start()
        self._server.start()

    def stop(self):
        self._server.stop()
        super().stop()

    def _create_web_server(self):
        self._server = WebEngine.add_server(
            self.web_server().port(), self.web_server().host())
        self._server.add_handler(
            BuildSignal(
                self.web_server().endpoint(),
                self.notify_signals,
                self.logger,
                self.webhook_secret()
            )
        )
