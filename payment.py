# ---------------------------------------
# payment.py

# By: Emmandra
# ----------------------------------------
import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment='sandbox',
        merchant_id='zpkjh3qg4wrd7j3c',
        public_key='mk49hp8wm7k5d449',
        private_key='1db41483e66e2ee4c182be8ddbbe7a43' 
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)