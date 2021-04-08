#!/Users/jollygama/miniconda3/bin/python
import pyetrade
import os
import pprint
import datetime
import webbrowser
import json


class ETrader:
    def __init__(self):
        print("Initializing ETrader...")
        self.pp = pprint.PrettyPrinter()
        self.init_etrade_auth()

    def init_etrade_auth(self):
        # prod_api_key == client_key
        # prod_secret == client_secret
        # app_api_key == resource_owner_key
        # app_api_secret == resource_owner_secret
        self.etrade_auth_keys = {}
        # Instantiate client key and secret
        with open("e-trade-prod-api-key.txt") as client_key_file:
            self.etrade_auth_keys["client_key"] = client_key_file.read().rstrip()
        with open("e-trade-prod-api-secret.txt") as client_secret_file:
            self.etrade_auth_keys["client_secret"] = client_secret_file.read().rstrip()

        # Check age of resource owner key and secret
        app_key_secret_mtime = datetime.datetime.fromtimestamp(
            os.stat("e-trade-app-api-key.txt").st_mtime
        )
        app_key_and_secret_age = datetime.datetime.now() - app_key_secret_mtime

        # Get new keys if we have old app/resource_owner keys
        if app_key_and_secret_age.total_seconds() >= 119 * 60:
            print(
                "E-Trade App API Key and Secret are older than 2 hours, requesting new tokens..."
            )
            # Get new request token from ETrade for new resource_owner key and secret
            self.oauth = pyetrade.ETradeOAuth(
                self.etrade_auth_keys["client_key"],
                self.etrade_auth_keys["client_secret"],
            )
            # Shows URL to get verfication code
            print("Go to the provided URL, approve access, and enter the token...")
            self.authorization_url = self.oauth.get_request_token()
            webbrowser.open(self.authorization_url, new=2)

            verifier_code = input("Enter verification code: ")
            tokens = self.oauth.get_access_token(verifier_code)
            self.etrade_auth_keys["resource_owner_key"] = tokens["oauth_token"]
            self.etrade_auth_keys["resource_owner_secret"] = tokens[
                "oauth_token_secret"
            ]
            with open("e-trade-app-api-key.txt", "w") as resource_owner_key_file:
                resource_owner_key_file.write(
                    self.etrade_auth_keys["resource_owner_key"]
                )
            with open("e-trade-app-api-secret.txt", "w") as resource_owner_secret_file:
                resource_owner_secret_file.write(
                    self.etrade_auth_keys["resource_owner_secret"]
                )
            print("Got ETrade Resource Owner Key and Secret Tokens!")

        else:
            with open("e-trade-app-api-key.txt") as resource_owner_key_file:
                self.etrade_auth_keys[
                    "resource_owner_key"
                ] = resource_owner_key_file.read().rstrip()
            with open("e-trade-app-api-secret.txt") as resource_owner_secret_file:
                self.etrade_auth_keys[
                    "resource_owner_secret"
                ] = resource_owner_secret_file.read().rstrip()

        print("Instantiating ETrade Access Manager...")
        self.access_man = pyetrade.authorization.ETradeAccessManager(
            self.etrade_auth_keys["client_key"],
            self.etrade_auth_keys["client_secret"],
            self.etrade_auth_keys["resource_owner_key"],
            self.etrade_auth_keys["resource_owner_secret"],
        )
        print("Renewing App/Resource Owner Key and Secret...")
        self.access_man.renew_access_token()

        print("Showing E-Trade Keys...")
        self.pp.pprint(self.etrade_auth_keys)
        print("========================")

    def login_and_list_accounts(self):
        self.accounts = pyetrade.ETradeAccounts(
            self.etrade_auth_keys["client_key"],
            self.etrade_auth_keys["client_secret"],
            self.etrade_auth_keys["resource_owner_key"],
            self.etrade_auth_keys["resource_owner_secret"],
            dev=False,
        )
        print("Showing E-Trade Accounts")
        self.pp.pprint(self.accounts.list_accounts(resp_format="json"))

    def init_market(self):
        print("Initializing ETrade Market...")
        self.market = pyetrade.ETradeMarket(
            client_key=self.access_man.client_key,
            client_secret=self.access_man.client_secret,
            resource_owner_key=self.access_man.resource_owner_key,
            resource_owner_secret=self.access_man.resource_owner_secret,
            dev=False,
        )

    def get_stock_history(self, ticker):
        print("Getting stock data since 2016 for ticker {}...".format(ticker))
        quote = self.market.get_quote([ticker], resp_format="json")
        self.pp.pprint(quote)


def main():
    etrader = ETrader()
    etrader.login_and_list_accounts()
    etrader.init_market()
    etrader.get_stock_history("AAPL")


if __name__ == "__main__":
    main()
