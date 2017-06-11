pragma solidity ^0.4.7;

import "OpenRegistryRules.sol";
import "OpenRegistry.sol";

contract BoardRoomInterface {
  function newProposal(string _name, uint _debatePeriod, address _destination, uint _value, bytes _calldata) returns (uint proposalID) {}
  function vote(uint _proposalID, uint _position) returns (uint voteWeight) {}
  function execute(uint _proposalID, string _calldata) {}
  function changeRules(address _rules) {}

  function voterAddressOf(uint _proposalID, uint _voteID) constant returns (address) {}
  function numVoters(uint _proposalID) constant returns (uint) {}
  function positionWeightOf(uint _proposalID, uint _position) constant returns (uint) {}
  function voteOf(uint _proposalID, address _voter) constant returns (uint, uint, uint) {}
  function hasVoted(uint _proposalID, address _voter) constant returns (bool) {}

  function destinationOf(uint _proposalId) public constant returns (address) {}
  function valueOf(uint _proposalId) public constant returns (uint) {}
  function hashOf(uint _proposalId) public constant returns (bytes32) {}
  function debatePeriodOf(uint _proposalId) public constant returns (uint) {}
  function createdOn(uint _proposalId) public constant returns (uint) {}
  function createdBy(uint _proposalId) public constant returns (address) {}

  event ProposalCreated(uint indexed _proposalID, address indexed _destination, uint indexed _value);
  event VoteCounted(address indexed _destination, uint indexed _position, address indexed _voter);
  // event ProposalExecuted(uint indexed _proposalID, address indexed _destination,address indexed _sender, bytes4 sig);
  event ProposalExecuted(uint indexed _proposalID, address indexed _destination, bytes4 indexed sig);
}

contract BoardRoom is BoardRoomInterface {

  function BoardRoom(address _rules, address _registry) {
    rules = Rules(_rules);
    registry = Registry(_registry);
  }

  modifier canpropose {
    if(rules.canPropose(msg.sender)) {
      _;
    }
  }

  modifier canvote (uint _proposalID) {
    if(rules.canVote(msg.sender, _proposalID)) {
      _;
    }
  }

  modifier haswon(uint _proposalID) {
    if(rules.hasWon(_proposalID)) {
      _;
    }
  }

  modifier onlyself() {
    if(msg.sender == address(this)) {
      _;
    }
  }
  
  /// @notice The contract fallback function
  function () payable public {}

  function newProposal(string _name, uint _debatePeriod, address _destination, uint _value, bytes _calldata) canpropose returns (uint proposalID) {
    proposalID = proposals.length;
    Proposal memory p;
    p.name = _name;
    p.destination = _destination;
    p.value = _value;
    p.hash = sha3(_destination, _value, _calldata);
    p.debatePeriod = _debatePeriod * 1 seconds;
    p.created = now;
    p.from = msg.sender;
    p.executed = false;
    proposals.push(p);
    ProposalCreated(proposalID, _destination, _value);
    return proposalID;
  }

  function vote(uint _proposalID, uint _position) canvote(_proposalID) returns (uint voterWeight) {
    voterWeight = rules.votingWeightOf(msg.sender, _proposalID);
    proposals[_proposalID].votes[msg.sender] = Vote({
      position: _position,
      weight: voterWeight,
      created: now
      });
    proposals[_proposalID].voters.push(msg.sender);
    proposals[_proposalID].positions[_position] += voterWeight;
    VoteCounted(proposals[_proposalID].destination, _position, msg.sender);
    return voterWeight;
  }

  function execute(uint _proposalID, string _calldata) haswon(_proposalID) {
    Proposal p = proposals[_proposalID];

    if(!p.executed
      && sha3(p.destination, p.value, _calldata) == p.hash) {
      p.executed = true;

      if(!p.destination.call.value(p.value)(bytes4(keccak256(_calldata)))){
          throw;
        }
        ProposalExecuted(_proposalID, p.destination, bytes4(keccak256(_calldata)));
      }
    }

    function changeRules(address _rules) onlyself {
      rules = Rules(_rules);
    }

    function destructSelf(address _destination) onlyself {
      selfdestruct(_destination);
    }


    function positionWeightOf(uint _proposalID, uint _position) constant returns (uint) {
      return proposals[_proposalID].positions[_position];
    }

    function voteOf(uint _proposalID, address _voter) constant returns (uint position, uint weight, uint created) {
      Vote v = proposals[_proposalID].votes[_voter];
      position = v.position;
      weight = v.weight;
      created = v.created;
    }

    function voterAddressOf(uint _proposalID, uint _voteID) constant returns (address) {
      return proposals[_proposalID].voters[_voteID];
    }

    function numVoters(uint _proposalID) constant returns (uint) {
      return proposals[_proposalID].voters.length;
    }

    function numProposals() constant returns (uint) {
      return proposals.length;
    }

    function hasVoted(uint _proposalID, address _voter) constant returns (bool) {
      if(proposals[_proposalID].votes[_voter].created > 0) {
        return true;
      }
    }

    function destinationOf(uint _proposalId) public constant returns (address) {
      return proposals[_proposalId].destination;
    }

    function valueOf(uint _proposalId) public constant returns (uint) {
      return proposals[_proposalId].value;
    }

    function hashOf(uint _proposalId) public constant returns (bytes32) {
      return proposals[_proposalId].hash;
    }

    function debatePeriodOf(uint _proposalId) public constant returns (uint) {
      return proposals[_proposalId].debatePeriod;
    }

    function createdOn(uint _proposalId) public constant returns (uint) {
      return proposals[_proposalId].created;
    }

    function createdBy(uint _proposalId) public constant returns (address) {
      return proposals[_proposalId].from;
    }

    struct Proposal {
      string name;
      address destination;
      uint value;
      bytes32 hash;
      bool executed;
      uint debatePeriod;
      uint created;
      address from;
      mapping(uint => uint) positions;
      mapping(address => Vote) votes;
      address[] voters;
    }

    struct Vote {
      uint position;
      uint weight;
      uint created;
    }

    Proposal[] public proposals;
    Rules public rules;
    Registry public registry;
  }
