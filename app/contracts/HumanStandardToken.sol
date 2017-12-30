pragma solidity ^0.4.7;

/*
This Token Contract implements the standard token functionality (https://github.com/ethereum/EIPs/issues/20) as well as the following OPTIONAL extras intended for use by humans.

In other words. This is intended for deployment in something like a Token Factory or Mist wallet, and then used by humans.
Imagine coins, currencies, shares, voting weight, etc.
Machine-based, rapid creation of many tokens would not necessarily need these extra features or will be minted in other manners.

1) Initial Finite Supply (upon creation one specifies how much is minted).
2) In the absence of a token registry: Optional Decimal, Symbol & Name.
3) Optional approveAndCall() functionality to notify a contract if an approval() has occurred.

.*/

import "StandardToken.sol";

contract HumanStandardToken is StandardToken {

    /* Public variables of the token */

    /*
    NOTE:
    The following variables are OPTIONAL vanities. One does not have to include them.
    They allow one to customise the token contract & in no way influences the core functionality.
    Some wallets/interfaces might not even bother to look at this information.
    */

    struct Order {
        uint256 amount; // in wei
        uint256 price; // in wei
    }

    uint256  public initialPrice;       // price of the token during ICO (in wei)
    uint256 public ownedPart;             // % of owned tokens by the sender
    string public name;                   //fancy name: eg Simon Bucks
    uint8 public decimals;                //How many decimals to show. ie. There could 1000 base units with 3 decimals. Meaning 0.980 SBX = 980 base units. It's like comparing 1 wei to 1 ether.
    string public symbol;                 //An identifier: eg SBX
    string public version = "H0.1";       //human 0.1 standard. Just an arbitrary versioning scheme.

    mapping (address => Order) buyOrders;
    mapping (address => Order) sellOrders;

    event BuyOrder(address indexed _from, uint256 indexed _amount, uint256 indexed _price);
    event SellOrder(address indexed _from, uint256 indexed _amount, uint256 indexed _price);

    function HumanStandardToken(
        uint256 _initialAmount,
        uint256 _initialPrice,
        uint256 _ownedPart,
        string _tokenName,
        uint8 _decimalUnits,
        string _tokenSymbol
        ) {
        if (_ownedPart > _initialAmount) {
            revert();
        }

        totalSupply = _initialAmount;                        // Update total supply
        initialPrice = _initialPrice;                          // price during the ico
        ownedPart = _ownedPart;                                // % owned by sender
        name = _tokenName;                                   // Set the name for display purposes
        decimals = _decimalUnits;                            // Amount of decimals for display purposes
        symbol = _tokenSymbol;                               // Set the symbol for display purposes
        balances[msg.sender] = _ownedPart;               // Give the owned part to the creator
        balances[this] = totalSupply - _ownedPart;         // give the rest to the contract itself
    }

    function buy(uint256 _amount, address _seller) payable returns (bool) {
        if (msg.value == 0) {
            throw;
        }
        // if address is 0x0, buy from contract at initial price
        if (_seller == address(0) || _seller == address(this)) {
            if (msg.value >= (_amount * initialPrice) &&
                balances[this] > _amount) {
                    return this.transfer(msg.sender, _amount);
                }
        } else {
            Order o = sellOrders[_seller];
            // else, find the order from <_seller> and see if msg.values matches
            // if it does, send tokens to the buyer and ether to the seller
            if (o.amount > 0 && msg.value >= (o.amount * o.price)) {
                if (this.transfer(msg.sender, _amount)) {
                    delete sellOrders[_seller];
                    return _seller.send(o.amount * o.price);
                }
                return false;
            } else {
                // if order does not exist, create a buy order and keep ether
                buyOrders[msg.sender] = Order({amount: _amount, price: msg.value / _amount});
                BuyOrder(msg.sender, _amount, msg.value / _amount);
                return true;
            }
        }
    }

    function sellTo(address _buyer) returns (bool) {
        // check if seller has enough tokens to sell
        // send tokens to buyer and remove order
        // send ether to the seller
        Order o = buyOrders[_buyer];
        if (o.amount <= 0 || balances[msg.sender] < o.amount) {
            return false;
        }
        balances[msg.sender] -= o.amount;
        balances[_buyer] += o.amount;
        delete buyOrders[_buyer];
        if (!msg.sender.send(o.amount * o.price)) {
            return false;
        }
        Transfer(msg.sender, _buyer, o.amount);
        return true;
    }

    function sell(uint256 _amount, uint256 _price) returns (bool) {
        // create a new sell order and keep tokens
        if (_amount <= 0 || _price <= 0) {
            return false;
        }
        balances[msg.sender] -= _amount;
        balances[address(this)] += _amount;
        sellOrders[msg.sender] = Order({amount: _amount, price: _price});
        SellOrder(msg.sender, _amount, _price);
        return true;
    }

    function cancelSellOrder() returns (bool) {
        Order o = sellOrders[msg.sender];
        if (o.amount <= 0) {
            return false;
        }
        return this.transfer(msg.sender, o.amount);
    }

    function cancelBuyOrder() returns (bool) {
        Order o = buyOrders[msg.sender];
        if (o.amount <= 0) {
            return false;
        }
        return msg.sender.send(o.amount * o.price);
    }

    // function getOwnerList() returns (address[]) {
	// 	address[] memory list = new address[](projects[0].numMembers);
	// 	uint j = 0;
	// 	for (uint i = 0; i<members.length; i++){
	// 		if (members[i].project == address(this)) {
	// 			list[j++] = members[i].member;
	// 		}
	// 	}
	// 	return list;
	// }

}
