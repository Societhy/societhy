pragma solidity ^0.4.7;

import {BaseProject as Project} from "BaseProject.sol";
import {mortal} from "library.sol";
import {BoardRoom} from "BoardRoom.sol";
import {Offer} from "Offer.sol";
import "Registry.sol";

contract Societhy is mortal, BoardRoom {
    /* define variable greeting of the type string */
    string name;

    mapping(address => uint) offerId;
    OfferData[] public offers;

    event DonationMade(address indexed member, uint indexed value, bool success);
    event ProjectCreated(address indexed newProjectAddress, string name);
    event OfferCreated(address indexed newProjectAddress, address indexed contractor);

    struct OfferData {
        Offer offerAddress;
        address contractor;
    }

    /* this runs when the contract is executed */
    function Societhy(string _name, address _rules, address _registry) BoardRoom(_rules, _registry) public {
        name = _name;
    }

    function createProject(string _name) cancreateproject {
        Project newProjectAddress = new Project(_name, address(rules), address(registry));

        registry.createProject(address(newProjectAddress));
        ProjectCreated(newProjectAddress, _name);
    }

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

        Offer(_destination).setVotingDeadline(now + p.debatePeriod);

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

    function execute(uint _proposalID, bytes _calldata) haswon(_proposalID) {
        Proposal p = proposals[_proposalID];

        if(!p.executed
          && sha3(p.destination, p.value, _calldata) == p.hash) {
          p.executed = true;

          if(!p.destination.call.value(p.value)(bytes4(keccak256(_calldata)))){
           // if(!p.destination.call.value(p.value)(_calldata)){
              throw;
          }
          ProposalExecuted(_proposalID, p.destination, _calldata);
      }
  }

  function createOffer(
    address _contractor,
    address _client,
    bytes32 _hashOfTheProposalDocument,
    uint _initialWithdrawal,
    uint128 _minDailyWithdrawalLimit,
    uint _payoutFreezePeriod,
    bool _isRecurrent,
    uint _duration,
    string _type) {
    Offer newOfferAddress = new Offer(_contractor,
        _client,
        _hashOfTheProposalDocument,
        _initialWithdrawal,
        _minDailyWithdrawalLimit,
        _payoutFreezePeriod,
        _isRecurrent,
        _duration,
        _type);
    uint id;

    offerId[newOfferAddress] = offers.length;
    id = offers.length++;
    offers[id] = OfferData({offerAddress: newOfferAddress, contractor: _contractor});

    OfferCreated(newOfferAddress, _contractor);
}

function cancelOffer() {

}

function donate() payable {
    if (address(registry) != 0 && msg.value > 0) {
        registry.madeDonation(msg.sender, msg.value);
    }
    DonationMade(msg.sender, msg.value, true);
}
}