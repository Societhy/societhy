pragma solidity ^0.4.7;

import "Registry.sol";

contract OpenRegistry is Registry {

	modifier onlyMembers {
		if (memberId[msg.sender] == 0) throw;
		_;
	}

	modifier projectExists(address _someProject) {
		for (uint i = 0; i<projects.length; i++) {
			if (projects[i] == _someProject) {
				_;
			}
		}
	}

	function OpenRegistry() public {
		members.push(Member({member: 0, donation: 0, tag: '', memberSince: now, project: address(0)}));
	}

	function register(address _someMember, string _tag) public returns (bool){
		uint id;
		if (memberId[_someMember] == 0) {
			memberId[_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now, project: address(0)});
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
	
	function createProject(address _project) public returns (bool) {
		projects.push(_project);
		return true;
	}

	function registerToProject(address _project, address _someMember, string _tag) projectExists(_project) public returns (bool) {
		uint id;
		if (projectMemberId[_project][_someMember] == 0) {
			projectMemberId[_project][_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now, project: address(this)});
			NewMember(_someMember, _tag);
			return true;
		}
		else throw;
	}

	function memberIdForProject(address _someProject, address _someMember) public returns (uint) {
		return projectMemberId[_someProject][_someMember];
	}

	function madeDonation(address _from, uint _value) {
		members[memberId[_from]].donation += _value;
	}

	function numMembers() public constant returns (uint) {
		return members.length;
	}

}
