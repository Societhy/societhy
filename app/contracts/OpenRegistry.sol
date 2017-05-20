pragma solidity ^0.4.7;

import "Registry.sol";

contract OpenRegistry is Registry {

	modifier onlyMembers {
		if (memberId[msg.sender] == 0) throw;
		_;
	}

	function OpenRegistry() public {
		members.push(Member({member: 0, donation: 0, tag: '', memberSince: now}));
	}

	function register(address _someMember, string _tag) public {
		uint id;
		if (memberId[_someMember] == 0) {
			memberId[_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now});
			NewMember(_someMember, _tag);
		}
		else throw;
	}

	function leave() onlyMembers /* modifier */{
		for (uint i = memberId[msg.sender]; i<members.length-1; i++){
			members[i] = members[i+1];
		}
		delete members[members.length-1];
		memberId[msg.sender] = 0;
		members.length--;
		MemberLeft(msg.sender);
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
