Stripe
======
Block to establish webserver and forwards data from a webhook configured in stripe  
A webhook endpoint needs to be configured in the Stripe Dashboard and forward to the web server created by the block.  

Properties
----------
- **web_server**: Web server configuration for webhook to post to
- **webhook_secret**: Webhook secrect from Stripe

Inputs
------
None

Outputs
-------
- **default**: Data sent from stripe.

Commands
--------
None

Dependencies
------------
stripe

