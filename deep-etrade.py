#!/Users/jollygama/miniconda3/bin/python
import pyetrade
import os
import pprint


class ETrader():
    def __init__(self):
        print("Initializing ETrader...")
        self.pp = pprint.PrettyPrinter()
        self.get_etrade_auth_keys()
        if self.etrade_auth_keys["app_api_key"] is None \
                and self.etrade_auth_keys["app_api_secret"] is None:
            print("Don't have app API key nor SECRET, need to request new ones...")
            self.get_request_token()
            self.get_access_token()

    def get_etrade_auth_keys(self):
        self.etrade_auth_keys = {}
        with open("e-trade-prod-api-key.txt") as prod_api_key:
            self.etrade_auth_keys["prod_api_key"] = prod_api_key.read(
            ).rstrip()
        with open("e-trade-prod-api-secret.txt") as prod_api_secret:
            self.etrade_auth_keys["prod_api_secret"] = prod_api_secret.read(
            ).rstrip()
        with open("e-trade-app-api-key.txt") as app_api_key:
            self.etrade_auth_keys["app_api_key"] = app_api_key.read().rstrip()
        with open("e-trade-app-api-secret.txt") as app_api_secret:
            self.etrade_auth_keys["app_api_secret"] = app_api_secret.read(
            ).rstrip()

        print("Reauthorizing app (resource) keys...")
        self.access_man = pyetrade.authorization.ETradeAccessManager(
            self.etrade_auth_keys["prod_api_key"],
            self.etrade_auth_keys["prod_api_secret"],
            self.etrade_auth_keys["app_api_key"],
            self.etrade_auth_keys["app_api_secret"]
        )
        self.access_man.renew_access_token()

        print("Showing E-Trade Keys...")
        self.pp.pprint(self.etrade_auth_keys)
        print("========================")

    def get_request_token(self):
        self.oauth = pyetrade.ETradeOAuth(
            self.etrade_auth_keys["prod_api_key"],
            self.etrade_auth_keys["prod_api_secret"])
        # Shows URL to get verfication code
        print("Go to the provided URL, approve access, and enter the token...")
        print(self.oauth.get_request_token())

    def get_access_token(self):
        verifier_code = input("Enter verification code: ")
        tokens = self.oauth.get_access_token(verifier_code)
        print("Got E_TRADE Access Tokens")
        print(tokens)

    def login_and_list_accounts(self):
        self.accounts = pyetrade.ETradeAccounts(
            self.etrade_auth_keys["prod_api_key"],
            self.etrade_auth_keys["prod_api_secret"],
            self.etrade_auth_keys["app_api_key"],
            self.etrade_auth_keys["app_api_secret"],
            dev=False)
        print("Showing E-Trade Accounts")
        self.pp.pprint(self.accounts.list_accounts())

    def get_stock_history(self, ticker):
        print("Getting stock data since 2016 for ticker {}...".format(ticker))


def main():
    etrader = ETrader()
    etrader.login_and_list_accounts()
    etrader.get_stock_history("AAPL")


if __name__ == "__main__":
    main()
