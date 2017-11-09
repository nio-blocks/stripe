import requests
import stripe
from nio import GeneratorBlock
from nio.signal.base import Signal
from nio.properties import VersionProperty, StringProperty, IntProperty, \
    PropertyHolder, ObjectProperty
from nio.modules.web import RESTHandler, WebEngine


class BuildSignal(RESTHandler):

    def __init__(self, endpoint, notify_signals, logger):
        super().__init__('/'+endpoint)
        self.notify_signals = notify_signals
        self.logger = logger

    def before_handler(self, req, rsp):
        # Overridden in order to skip the authentication in the framework
        return

    def on_post(self, req, rsp):
        payload = req.get_body()
        received_sig = req.headers.get('Stripe-Signature', None)
        if not isinstance(payload, dict):
            self.logger.error("Invalid JSON in body: {}".format(payload))
            return
        try:
            event = stripe.Webhook.construct_event(
                payload, received_sig, self.webhook_token())
        except ValueError:
            self.logger.error('Error decoding payload')
        except stripe.error.SignatureVerificationError:
            self.logger.error('Invalid signature')

        self.notify_signals([Signal(payload)])


class WebServer(PropertyHolder):

    host = StringProperty(title='Host', default='0.0.0.0')
    port = IntProperty(title='Port', default=8182)
    endpoint = StringProperty(title='Endpoint', default='')


class Stripe(GeneratorBlock):

    version = VersionProperty('0.1.0')
    web_server = ObjectProperty(
        WebServer, title='Web Server', default=WebServer())
    # callback_url = StringProperty(
    #     title="Callback URL", default="https://example.org/hooks/1")
    access_token = StringProperty(
        title="Access Token", default="[[STRIPE_ACCESS_TOKEN]]")
    webhook_token = StringProperty(
        title="Stripe Webhook Token", default="[[STRIPE_WEBHOOK_TOKEN]]")

    def __init__(self):
        super().__init__()
        self._server = None
        self._subscription_id = None

    def configure(self, context):
        super().configure(context)
        self._create_web_server()
        stripe.api_key = self.access_token()

        # TODO: What should post body to Stripe look like?
            # Does it need it?
        # response = self._request('post', body={
        #     "service_type": "web",
        #     "topics": ["conversation.user.created"],
        #     "url": self.callback_url(),
        # })
        # if response.status_code != 200:
        #     raise Exception
        # self._subscription_id = response.json()["id"]

    def start(self):
        super().start()
        self._server.start()

    def stop(self):
        # TODO: What should 'delete' request to Stripe look like?
        # self._request('delete', id=self._subscription_id)
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
            )
        )

    # def _request(self, method='post', id=None, body=None):
    #     TODO: What is the Stripe url?
            # Hopefully taken care of by the stripe library?

        # url = 'https://api.intercom.io/subscriptions'
        # if id:
        #     url += "/{}".format(id)
        # kwargs = {}
        # kwargs['headers'] = {
        #     "Authorization": "Bearer {}".format(self.access_token()),
        #     "Accept": "application/json",
        #     "Content-Type": "application/json",
        # }
        # if body:
        #     kwargs['json'] = body
        # response = getattr(requests, method)(url, **kwargs)
        # if response.status_code != 200:
        #     self.logger.error("Http request failed: {} {}".format(
        #         response, response.json()))
        # self.logger.debug("Http response: {}".format(response.json()))
        # return response
