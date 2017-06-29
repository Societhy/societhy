pragma solidity ^0.4.7;

import "Registry.sol";

contract ControlledRegistry is Registry {

	event PermissionChanged(address indexed member, bool right);

	modifier onlyAllowed {
		if (rights[msg.sender] != true) throw;
		_;
	}

	modifier onlyProjectMembers(address _someProject) {
		if (projectMemberId[_someProject][msg.sender] == 0) throw;
		_;
	}

	modifier projectExists(address _someProject) {
		if (projectId[_someProject] == 0) throw;
		_;
	}


	function ControlledRegistry() public {
		members.push(Member({member: 0, donation: 0, tag: '', memberSince: now, project: address(0)}));
		projects.push(ProjectData({project: address(this), numMembers: 0}));
		owner = msg.sender;
		rights[msg.sender] = true;
		rights[this] = true;
	}

	function register(address _someMember, string _tag) public returns (bool) {
		uint id;
		if (memberId[_someMember] == 0) {
			memberId[_someMember] = members.length;
			id = members.length++;
			members[id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now, project: address(this)});
			projects[0].numMembers += 1;
			rights[_someMember] = true;
			NewMember(_someMember, _tag);
			return true;
		}
		else throw;
	}

	function leave(address _someMember) public onlyAllowed  {
		for (uint i = memberId[_someMember]; i<members.length-1; i++){
			members[i] = members[i+1];
		}
		delete members[members.length-1];
		memberId[_someMember] = 0;
		projects[0].numMembers -= 1;
		delete rights[_someMember];
		members.length--;
		MemberLeft(_someMember);
	}

	function createProject(address _project) onlyAllowed public returns (bool) {
		uint id;
		if (projectId[_project] == 0) {
			projectId[_project] = projects.length;
			id = projects.length++;
			projects[id] = ProjectData({project: _project, numMembers: 0});
			return true;
		}
		else throw;
	}

	function joinProject(address _project, address _someMember, string _tag) public returns (bool) {
		uint m_id;
		if (projectMemberId[_project][_someMember] == 0) {
			projectMemberId[_project][_someMember] = members.length;
			m_id = members.length++;
			members[m_id] = Member({member: _someMember, donation: 0, tag: _tag, memberSince: now, project: address(this)});
			projects[projectId[_project]].numMembers += 1;
			NewMember(_someMember, _tag);
			return true;
		}
		else throw;
	}


	function leaveProject(address _project, address _someMember) onlyProjectMembers(_project) public returns (bool)/* modifier */{
		for (uint i = projectMemberId[_project][_someMember]; i<members.length-1; i++){
			members[i] = members[i+1];
		}
		delete members[members.length-1];
		projectMemberId[_project][_someMember] = 0;
		projects[projectId[_project]].numMembers -= 1;	
		members.length--;
		MemberLeft(_someMember);
	}


	function memberIdForProject(address _someProject, address _someMember) public returns (uint) {
		return projectMemberId[_someProject][_someMember];
	}
	
	function getMemberList() returns (address[]) {
		address[] memory list = new address[](projects[0].numMembers);
		uint j = 0;
		for (uint i = 0; i<members.length; i++){
			if (members[i].project == address(this)) {
				list[j++] = members[i].member;
			}
		}
		return list;
	}

	function getMemberListForProject(address _someProject) returns (address[]) {
		address[] memory list = new address[](projects[projectId[_someProject]].numMembers);
		uint j = 0;

		for (uint i = 0; i<members.length; i++){
			if (members[i].project == _someProject) {
				list[j++] = members[i].member;
			}
		}
		return list;
	}

	function allow(address _someMember) public onlyAllowed {
		rights[_someMember] = true;
		PermissionChanged(_someMember, true);
	}

	function isAllowed(address _someMember) public constant returns (bool) {
		return rights[_someMember];
	}

	function madeDonation(address _from, uint _value) {
		members[memberId[_from]].donation += _value;
	}

	function numMembers() public constant returns (uint) {
		return members.length;
	}

}
