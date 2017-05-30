pragma solidity ^0.4.7;

contract Registry {
	mapping (address => uint) public memberId;
	Member[] public members;

	event NewMember(address indexed member, string tag);
	event MemberLeft(address indexed member);

	struct Member {
		address member;
		uint donation;
		string tag;
		uint memberSince;
	}

	function register(address _someMember, string _tag) public;
	function leave();
	function getMemberList() returns (address[]);
	function madeDonation(address from, uint value);
	function numMembers() public constant returns (uint);

}
