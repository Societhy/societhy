pragma solidity ^0.4.7;

contract Registry {
	mapping (address => uint) public memberId;
	mapping (address =>	mapping(address => uint)) public projectMemberId; 

	Member[] public members;
	address[] public projects;
	address owner;

	// mapping(address => mapping(bytes4 => bool)) rights;
	mapping(address => bool) public rights;


	event NewMember(address indexed member, string tag);
	event MemberLeft(address indexed member);

	struct Member {
		address member;
		uint donation;
		string tag;
		uint memberSince;
		address project;
	}

	function register(address _someMember, string _tag) public returns (bool);
	function leave(address _someMember);
	function getMemberList() returns (address[]);

	function createProject(address _someProject) public returns (bool);
	function registerToProject(address _project, address _someMember, string _tag) public returns (bool);

	function memberIdForProject(address _someProject, address _someMember) public returns (uint);

	function madeDonation(address from, uint value);
	function numMembers() public constant returns (uint);
}
