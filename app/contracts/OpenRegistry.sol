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

	function register(address _someMember, string _tag) public returns (bool){
		uint id;
		if (memberId[_someMember] == 0) {
			memberId[_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now});
			NewMember(_someMember, _tag);
			return true;
		}
		else throw;
	}

	function leave(address _someMember) onlyMembers /* modifier */{
		for (uint i = memberId[_someMember]; i<members.length-1; i++){
			members[i] = members[i+1];
		}
		delete members[members.length-1];
		memberId[_someMember] = 0;
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
