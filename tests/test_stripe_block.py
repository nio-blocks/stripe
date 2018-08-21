import json
from unittest.mock import MagicMock, patch

from nio.testing.block_test_case import NIOBlockTestCase
from ..stripe_block import Stripe, BuildSignal


class TestBuildSignal(NIOBlockTestCase):

    def test_web_handler_post_dict(self):
        notify_signals = MagicMock()
        handler = BuildSignal(endpoint='',
                              notify_signals=notify_signals,
                              logger=MagicMock(),
                              webhook_secret='superSecret')
        request = MagicMock()
        request._body.read.return_value.decode.return_value = '{"Im a": "dictionary"}'

        with patch(BuildSignal.__module__ + '.stripe') as mock_stripe:
            handler.on_post(request, MagicMock())
            self.assertDictEqual(
                notify_signals.call_args[0][0][0].to_dict(),
                {"Im a": "dictionary"})


class TestStripeBlock(NIOBlockTestCase):

    def test_web_server_created(self):
        blk = Stripe()

        with patch(Stripe.__module__ + '.WebEngine') as mock_engine:
            with patch(Stripe.__module__ + '.BuildSignal') as mock_handler:
                self.configure_block(blk, {})
                mock_engine.add_server.assert_called_once_with(
                    blk.web_server().port(),
                    blk.web_server().host(),
                )
                mock_handler.assert_called_once_with(
                    blk.web_server().endpoint(),
                    blk.notify_signals,
                    blk.logger,
                    blk.webhook_secret()
                )
