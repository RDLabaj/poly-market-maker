from poly_market_maker.contracts import Contracts
from poly_market_maker.gas import GasStation, GasStrategy  
from poly_market_maker.utils import setup_web3
import os

# Setup
private_key = os.getenv('PRIVATE_KEY', 'YOUR_PRIVATE_KEY_HERE')
rpc_url = 'https://polygon-mainnet.infura.io/v3/10180878ecaa4339983a14ff65da80a4'
web3 = setup_web3(rpc_url, private_key)
address = web3.eth.account.from_key(private_key).address

gas_station = GasStation(GasStrategy('fixed'), web3, None, 25)
contracts = Contracts(web3, gas_station)

# Native USDC (co powinien używać bot)
native_usdc = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359' 
# Bridged USDC.e (co faktycznie mamy)
bridged_usdc = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'

print(f'Address: {address}')
print(f'Native USDC balance: {contracts.token_balance_of(native_usdc, address)}')
print(f'Bridged USDC.e balance: {contracts.token_balance_of(bridged_usdc, address)}') 