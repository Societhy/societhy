pragma solidity ^0.4.7;

import {basic_project as Project} from "basic_project.sol";
import {mortal, open_structure} from "library.sol";
import {BoardRoom} from "Boardroom.sol";

contract basic_orga is mortal, open_structure, BoardRoom {
    /* define variable greeting of the type string */
    string name;
 
    mapping (address => uint) public projectId;
    ProjectData[] public projects;

    event newDonation(address indexed member, uint indexed value, bool success);
    event newProject(address indexed newProjectAddress, string name);

    struct ProjectData {
        Project projectAddress;
        string  name;
    }

   /* this runs when the contract is executed */
    function basic_orga(string _name, address _rules) BoardRoom(_rules) public {
        name = _name;
        members.push(Member({member: 0, donation: 0, name: '', memberSince: now}));
        projects.push(ProjectData({projectAddress: new Project(''), name: ''}));
    }

    function createProject(string _name) {
        Project newProjectAddress = new Project(_name);
        uint id;

        projectId[newProjectAddress] = projects.length;
        id = projects.length++;
        projects[id] = ProjectData({projectAddress: newProjectAddress, name: _name});

        newProject(newProjectAddress, _name);
    }

    function donate() payable {
        if (memberId[msg.sender] != 0 && msg.value > 0) {
            members[memberId[msg.sender]].donation += msg.value;
        }
        newDonation(msg.sender, msg.value, true);
    }
}