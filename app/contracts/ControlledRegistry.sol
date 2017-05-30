pragma solidity ^0.4.7;

import "Registry.sol";

contract ControlledRegistry is Registry {

	address owner;

	// mapping(address => mapping(bytes4 => bool)) rights;
	mapping(address => bool) public rights;

	modifier onlyAllowed {
		if (rights[msg.sender] != true) throw;
		_;
	}

	function ControlledRegistry() public {
		members.push(Member({member: 0, donation: 0, tag: '', memberSince: now}));
		owner = msg.sender;
		rights[msg.sender] = true;
	}

	function register(address _someMember, string _tag) public onlyAllowed {
		uint id;
		if (memberId[_someMember] == 0) {
			memberId[_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now});
			NewMember(_someMember, _tag);
		}
		else throw;
	}

	function leave(address _someMember) public onlyAllowed  {
		for (uint i = memberId[_someMember]; i<members.length-1; i++){
			members[i] = members[i+1];
		}
		delete members[members.length-1];
		memberId[_someMember] = 0;
		delete rights[_someMember];
		members.length--;
		MemberLeft(_someMember);
	}

	function getMemberList() returns (address[]) {
		address[] memory list = new address[](members.length);

		for (uint i = 0; i<members.length; i++){
			list[i] = members[i].member;
		}
		return list;
	}

	function madeDonation(address _from, uint _value) {
		members[memberId[_from]].donation += _value;
	}

	function numMembers() public constant returns (uint) {
		return members.length;
	}

}
