pragma solidity ^0.4.7;

contract mortal {
    /* Define variable owner of the type address*/
    address owner;

    /* this function is executed at initialization and sets the owner of the contract */
    function mortal() { owner = msg.sender; }

    /* Function to recover the funds on the contract */
    function kill() { if (msg.sender == owner) selfdestruct(owner); }

    modifier onlyOwner {
        if (msg.sender != owner) throw;
        _;
    }
}

contract basic_orga is mortal {
    /* define variable greeting of the type string */
    string name;
    mapping (address => uint) public memberId;
    Member[] public members;
 
    event newMember(address indexed member);
    event memberLeft(address indexed member);
    event newDonation(address indexed member, uint indexed value);

    struct Member {
        address member;
        uint donation;
        string name;
        uint memberSince;
    }

    modifier onlyMembers {
        if (memberId[msg.sender] == 0) throw;
        _;
    }

    /* this runs when the contract is executed */
    function basic_orga(string _name) public {
        name = _name;
        members.push(Member({member: 0, donation: 0, name: '', memberSince: now}));
    }

    function join(string _name) public {
        uint id;
        if (memberId[msg.sender] == 0) {
            memberId[msg.sender] = members.length;
            id = members.length++;
            members[id] = Member({member: msg.sender, donation: 0, name: _name, memberSince: now});
            newMember(msg.sender);
        }
        else throw;
    }

    function leave() onlyMembers /* modifier */{
        for (uint i = memberId[msg.sender]; i<members.length-1; i++){
            members[i] = members[i+1];
        }
        delete members[members.length-1];
        members.length--;
        memberLeft(msg.sender);
    }

    function donate() payable public {
        // if (msg.value == 0) throw;
        // else {
        //     if (memberId[msg.sender] == 0) {
        //         members[memberId[msg.sender]].donation += msg.value;
        //     }
        newDonation(msg.sender, msg.value);
        // }
    }

    function getMemberList() returns (address[]) {
        address[] memory list = new address[](members.length);

        for (uint i = 0; i<members.length; i++){
           list[i] = members[i].member;
        }
        return list;
    }

    /* main function */
    function getName() constant returns (string) {
        return name;
    }
}