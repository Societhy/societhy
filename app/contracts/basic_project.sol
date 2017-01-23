pragma solidity ^0.4.7;

import {mortal, open_structure} from "library.sol";

contract basic_project is mortal, open_structure {
    /* define variable greeting of the type string */
    string name;

    event newDonation(address indexed member, uint indexed value, bool success);

    /* this runs when the contract is executed */
    function basic_project(string _name) public {
        name = _name;
        members.push(Member({member: 0, donation: 0, name: '', memberSince: now}));
    }

    function donate() payable {
        if (msg.value == 0) throw;
        else {
            if (memberId[msg.sender] != 0) {
                members[memberId[msg.sender]].donation += msg.value;
            }
            newDonation(msg.sender, msg.value, true);
       }
    }
}