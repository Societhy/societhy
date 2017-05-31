pragma solidity ^0.4.7;

import {basic_project as Project} from "basic_project.sol";
import {mortal} from "library.sol";
import {BoardRoom} from "BoardRoom.sol";
import {Offer} from "Offer.sol";

contract Societhy is mortal, BoardRoom {
    /* define variable greeting of the type string */
    string name;

    mapping(address => uint) offerId;
    OfferData[] public offers;

    mapping (address => uint) public projectId;
    ProjectData[] public projects;

    event DonationMade(address indexed member, uint indexed value, bool success);
    event ProjectCreated(address indexed newProjectAddress, string name);
    event OfferCreated(address indexed newProjectAddress, address indexed contractor);

    struct OfferData {
        Offer offerAddress;
        address contractor;
    }

    struct ProjectData {
        Project projectAddress;
        string  name;
    }

    /* this runs when the contract is executed */
    function Societhy(string _name, address _rules, address _registry) BoardRoom(_rules, _registry) public {
        name = _name;
        projects.push(ProjectData({projectAddress: new Project(''), name: ''}));
    }

    function createProject(string _name) {
        Project newProjectAddress = new Project(_name);
        uint id;

        projectId[newProjectAddress] = projects.length;
        id = projects.length++;
        projects[id] = ProjectData({projectAddress: newProjectAddress, name: _name});

        ProjectCreated(newProjectAddress, _name);
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
        // if (address(registry) != 0
        //      && registry.memberId(msg.sender) != 0 && msg.value > 0) {
        //     registry.madeDonation(msg.sender, msg.value);
        // }
        DonationMade(msg.sender, msg.value, true);
    }
}