/*
This file is part of the Societhy.

The Societhy is free software: you can redistribute it and/or modify
it under the terms of the GNU lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

The Societhy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU lesser General Public License for more details.

You should have received a copy of the GNU lesser General Public License
along with the Societhy.  If not, see <http://www.gnu.org/licenses/>.
*/


/*
  An Offer from a Contractor to the Societhy. No logic about the Societhy reward is
  included in this contract.

  Feel free to use as a base contract for your own proposal.

  Actors:
  - Offerer:    the entity that creates the Offer. Usually it is the initial
                Contractor.
  - Contractor: the entity that has rights to withdraw ether to perform
                its project.
  - Client:     the Societhy that gives ether to the Contractor. It accepts
                the Offer, can adjust daily withdraw limit or even fire the
                Contractor.
*/
pragma solidity ^0.4.7;

import "./Societhy.sol";

contract Offer {

    // Period of time after the passing of a proposal during which the offer
    // contract can not be signed in order to provide enough time to anyone
    // who may want to split off the Societhy to do so.
    uint constant splitGracePeriod = 8 days;

    // Initial withdrawal to the Contractor. It is done the moment the
    // Offer is accepted. Set once by the Offerer.
    uint initialWithdrawal;

    // The minimum daily withdrawal limit that the Contractor accepts.
    // Set once by the Offerer.
    uint128 minDailyWithdrawalLimit;

    // The amount of wei the Contractor has right to withdraw daily above the
    // initial withdrawal. The Contractor does not have to perform the
    // withdrawals every day as this amount accumulates.
    uint128 dailyWithdrawalLimit;

    // Period of time after which money can be withdrawn from this contract
    uint payoutFreezePeriod;

    // The address of the Contractor.
    address contractor;

    // The hash of the Proposal/Offer document.
    bytes32 hashOfTheProposalDocument;

    // The time of the last withdrawal to the Contractor.
    uint lastWithdrawal;

    // The timestamp when the offer contract was accepted.
    uint dateOfSignature;

    // Voting deadline of the proposal
    uint votingDeadline;

    // The address of the current Client.
    Societhy client;
    // The address of the Client who accepted the Offer.
    Societhy originalClient;

    // Flag denoting whether the contract is still considered valid
    bool isContractValid;

    // Flag denoting if the initial withdrawal sum was drawn from the contract
    bool initialWithdrawalDone;

    // Flag denoting if money can be withdrawn from the client after creation
    bool isRecurrent;

    // if isRecurrent is set to True, then contractor is able to withdraw money for <duration> days
    uint duration;

    uint creationDate;

    // type of offer, can be 'investment', 'employment', 'tax', 'service'
    string offerType;

    mapping(address => bool) actors;

    event FundsWithdrawn(address indexed contractor, uint indexed withdrawalAmount);

    modifier onlyClient {
        if (msg.sender != address(client))
            throw;
        _;
    }

    // Prevents methods from perfoming any value transfer
    modifier noEther() {if (msg.value > 0) throw; _;}

    function Offer(
        address _contractor,
        address _client,
        bytes32 _hashOfTheProposalDocument,
        uint _initialWithdrawal,
        uint128 _minDailyWithdrawalLimit,
        uint _payoutFreezePeriod,
        bool _isRecurrent,
        uint _duration,
        string _type) {
        contractor = _contractor;
        originalClient = Societhy(_client);
        client = Societhy(_client);
        hashOfTheProposalDocument = _hashOfTheProposalDocument;
        initialWithdrawal = _initialWithdrawal;
        minDailyWithdrawalLimit = _minDailyWithdrawalLimit;
        dailyWithdrawalLimit = _minDailyWithdrawalLimit;
        payoutFreezePeriod = _payoutFreezePeriod;
        isRecurrent = _isRecurrent;
        duration = _duration * 1 minutes;
        creationDate = now;
        offerType = _type;
    }

    // non-value-transfer getters

    function getInitialWithdrawal() noEther constant returns (uint) {
        return initialWithdrawal;
    }

    function getMinDailyWithdrawalLimit() noEther constant returns (uint128) {
        return minDailyWithdrawalLimit;
    }

    function getDailyWithdrawalLimit() noEther constant returns (uint128) {
        return dailyWithdrawalLimit;
    }

    function getCreationDate() noEther constant returns (uint) {
        return creationDate;
    }

    function getPayoutFreezePeriod() noEther constant returns (uint) {
        return payoutFreezePeriod;
    }

    function getContractor() noEther constant returns (address) {
        return contractor;
    }

    function getHashOfTheProposalDocument() noEther constant returns (bytes32) {
        return hashOfTheProposalDocument;
    }

    function getLastWithdrawal() noEther constant returns (uint) {
        return lastWithdrawal;
    }

    function getDateOfSignature() noEther constant returns (uint) {
        return dateOfSignature;
    }

    function getClient() noEther constant returns (Societhy) {
        return client;
    }

    function getIsRecurrent() noEther constant returns (bool) {
        return isRecurrent;
    }

    function getDuration() noEther constant returns (uint) {
        return duration;
    }

    function getOriginalClient() noEther constant returns (Societhy) {
        return originalClient;
    }

    function getIsContractValid() noEther constant returns (bool) {
        return isContractValid;
    }

    function getInitialWithdrawalDone() noEther constant returns (bool) {
        return initialWithdrawalDone;
    }

    function getVotingDeadline() noEther constant returns (uint) {
        return votingDeadline;
    }

    function getOfferType() noEther constant returns (string) {
        return offerType;
    }

    function sign() public payable returns (bool) {
        if (msg.sender != address(originalClient) // no good samaritans give us ether
            || msg.value < initialWithdrawal    // no under/over payment
            || dateOfSignature != 0      // don't accept twice
            || votingDeadline == 0 )      // votingDeadline needs to be set
            //|| now < votingDeadline + splitGracePeriod) // give people time to split
            throw;

        lastWithdrawal = votingDeadline + payoutFreezePeriod;
        if (payoutFreezePeriod == 0) {
            if (!contractor.send(initialWithdrawal))
                throw;
            initialWithdrawalDone = true;
        }
        dateOfSignature = now;
        isContractValid = true;
        return true;
    }

    // Once a proposal is submitted, the client (=Societhy orga) should call this
    // function to set the voting deadline of the proposal
    function setVotingDeadline(uint _votingDeadline) noEther {
        if (msg.sender != address(client) || votingDeadline != 0)
            throw;

        votingDeadline = _votingDeadline;
    }

    function setDailyWithdrawLimit(uint128 _dailyWithdrawalLimit) onlyClient noEther {
        if (_dailyWithdrawalLimit >= minDailyWithdrawalLimit)
            dailyWithdrawalLimit = _dailyWithdrawalLimit;
    }

    // Terminate the ongoing Offer.
    //
    // The Client can terminate the ongoing Offer using this method. Using it
    // on an invalid (balance 0) Offer has no effect. The Contractor loses
    // right to any ether left in the Offer.
    function terminate() noEther onlyClient {
        if (originalClient.send(this.balance))
            isContractValid = false;
    }

    // Withdraw to the Contractor.
    //
    // Withdraw the amount of ether the Contractor has right to according to
    // the current withdraw limit.
    // Executing this function before the Offer is accepted by the Client
    // makes no sense as this contract has no ether.
    function withdraw() noEther {
        if (msg.sender != contractor || now < votingDeadline + payoutFreezePeriod)
            throw;
        uint timeSincelastWithdrawal = now - lastWithdrawal;
        // // // Calculate the amount using 1 second precision.
        uint amount = (timeSincelastWithdrawal * dailyWithdrawalLimit) / (1 days);
        if (amount > this.balance) {
            amount = this.balance;
        }
        var lastWithdrawalReset = lastWithdrawal;
        lastWithdrawal = now;
        if (amount < 0.0001 ether || !contractor.send(amount)) {
            lastWithdrawal = lastWithdrawalReset;
            FundsWithdrawn(contractor, 0);
        }
        FundsWithdrawn(contractor, amount);
    }

    // Perform the withdrawal of the initial sum of money to the contractor
    // if that did not already happen during the signing
    function performInitialWithdrawal() noEther {
        if (msg.sender != contractor
            || now < votingDeadline + payoutFreezePeriod
            || initialWithdrawalDone ) {
            throw;
        }

        initialWithdrawalDone = true;
        if (!contractor.send(initialWithdrawal))
            throw;
    }

    // Change the client Societhy by giving the new Societhy's address
    // warning: The new Societhy must come either from a split of the original
    // Societhy or an update via `newContract()` so that it can claim rewards
    function updateClientAddress(Societhy _newClient) onlyClient noEther {
        client = _newClient;
    }

    function () {
        throw; // This is a business contract, no donations.
    }
}