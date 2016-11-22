import pytest

from app.core import wallet

def test_refresh_balance():
	user = {"eth": {
				"mainKey": "0xf2d2aff1320476cb8c6b607199d23175cc595693"
		}
	}
	print(user)
	assert wallet.refresh_balance(user) == 1599498197577
