# --------------------------------------------------------------------------
# bookExchange.py
# book-exchange flask file, that works as web-framework
# Author: Toussaint, Tiana, Emmandra
# -----------------------------------------------------------------------

from venmo_api import Client


def main():

    access_token = Client.get_access_token(username='emmandrawright@yahoo.com',
                                               password='Darrell1')

    return access_token

#-------------------------------------------------------------------
if __name__ == '__main__':
    main()
