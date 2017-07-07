pragma solidity ^0.4.7;

import {mortal, open_structure} from "library.sol";
import "Rules.sol";
import "Societhy.sol";
import "Registry.sol";

contract BaseProject is mortal {
    /* define variable greeting of the type string */
    string name;
    Poll[] public polls;
    Rules rules;
    Registry registry;
    uint created;
    uint duration;

    struct Poll {
      string subject;
      address destination;
      uint value;
      bool executed;
      uint debatePeriod;
      uint created;
      address from;
      mapping(uint => uint) positions;
      mapping(address => Vote) votes;
      address[] voters;
      bool isAnonymous;
      bool isPublic;
  }

  struct Vote {
      uint position;
      uint weight;
      uint created;
  }

  event DonationMade(address indexed member, uint indexed value, bool success);
  event VoteCounted(address indexed _destination, uint indexed _position, address indexed _voter);
  event PollCreated(address indexed from, uint indexed pollId);


  modifier canpoll {
    if(rules.canPoll(address(this), msg.sender)) {
      _;
  }
}

modifier canvotepoll (uint _pollID) {
  uint created = this.createdOn(_pollID);
  uint debatePeriod = this.debatePeriodOf(_pollID);

  if ( ((!polls[_pollID].isPublic && rules.canVoteInPoll(address(this), msg.sender)) || polls[_pollID].isPublic)
      && now < created + debatePeriod
      && !this.hasVoted(_pollID, msg.sender)) {
      _;
  }
}

/* this runs when the contract is executed */
function BaseProject(string _name, address rules_addr, address registry_addr, uint _duration) public {
    name = _name;
    rules = Rules(rules_addr);
    registry = Registry(registry_addr);
    duration = _duration * 1 minutes;
    created = now;
}

function newPoll(string _subject, address _destination, uint _value, uint _debatePeriod, bool _anonymous, bool _public) canpoll public returns (uint pollID) {
    pollID = polls.length;
    Poll memory p;
    p.subject = _subject;
    p.destination = _destination;
    p.value = _value;
    p.debatePeriod = _debatePeriod * 1 seconds;
    p.created = now;
    p.from = msg.sender;
    p.executed = false;
    p.isAnonymous = _anonymous;
    p.isPublic = _public;
    polls.push(p);

    PollCreated(p.from, pollID);
    return pollID;

}

function vote(uint _pollID, uint _position) canvotepoll(_pollID) public returns (uint voterWeight) {
    voterWeight = 1;
    if (!polls[_pollID].isAnonymous) {
        polls[_pollID].votes[msg.sender] = Vote({
          position: _position,
          weight: voterWeight,
          created: now
          });
        polls[_pollID].voters.push(msg.sender);
    }
    polls[_pollID].positions[_position] += voterWeight;
    VoteCounted(polls[_pollID].destination, _position, msg.sender);
    return voterWeight;

}

function getPoll(uint _pollID) public returns (uint yea, uint nay) {
    return (polls[_pollID].positions[1], polls[_pollID].positions[0]);
}

function debatePeriodOf(uint _pollID) public constant returns (uint) {
  return polls[_pollID].debatePeriod;
}

function getCreationDate() public constant returns (uint) {
  return created;
}

function getDuration() public constant returns (uint) {
  return duration;
}

function createdOn(uint _pollID) public constant returns (uint) {
  return polls[_pollID].created;
}

function hasVoted(uint _pollID, address _voter) constant returns (bool) {
    if(polls[_pollID].votes[_voter].created > 0) {
        return true;
    }
}

function donate() payable {
    if (address(registry) != 0 && msg.value > 0) {
        registry.madeDonation(msg.sender, msg.value);
    }
    DonationMade(msg.sender, msg.value, true);
}

}