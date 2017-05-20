pragma solidity ^0.4.7;

import "Registry.sol";

contract Rules {
	
	Registry public registry;
	
	mapping (address => uint) public memberId;

	event NewMember(address indexed member, string tag);
	event MemberLeft(address indexed member);

	function hasWon(uint _proposalID) public constant returns (bool);
	function canVote(address _sender, uint _proposalID) public constant returns (bool);
	function canPropose(address _sender) public constant returns (bool);
	function votingWeightOf(address _sender, uint _proposalID) public constant returns (uint);
}
