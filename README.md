Stripe
======
Block to establish webserver and forwards data from a webhook configured in stripe.  
An webhook endpoint needs to be configured in the Stripe Dashboard and forward to the web server created by the block. 

Properties
----------
- **access_token**: Access key from Stripe dashboard
- **web_server**: Web server configuration for webhook to post to

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

