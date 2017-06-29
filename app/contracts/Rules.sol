pragma solidity ^0.4.7;

import "Registry.sol";

contract Rules {
	
	Registry public registry;
	
	function hasWon(uint _proposalID) public constant returns (bool);
	function canVote(address _sender, uint _proposalID) public constant returns (bool);
	function canPropose(address _sender) public constant returns (bool);
	function canCreateProject(address _sender) public constant returns (bool);
	function canPoll(address _project, address _sender) public constant returns (bool);
	function canVoteInPoll(address _project, address _sender) public constant returns (bool);

	function votingWeightOf(address _sender, uint _proposalID) public constant returns (uint);
}
