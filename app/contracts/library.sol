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

contract open_structure {

    mapping (address => uint) public memberId;
    Member[] public members;

    event newMember(address indexed member, string tag);
    event memberLeft(address indexed member);

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

    function join(string _name, string tag) public {
        uint id;
        if (memberId[msg.sender] == 0) {
            memberId[msg.sender] = members.length;
            id = members.length++;
            members[id] = Member({member: msg.sender, donation: 0, name: _name, memberSince: now});
            newMember(msg.sender, tag);
        }
        else throw;
    }

    function leave() onlyMembers /* modifier */{
        for (uint i = memberId[msg.sender]; i<members.length-1; i++){
            members[i] = members[i+1];
        }
        delete members[members.length-1];
        memberId[msg.sender] = 0;
        members.length--;
        memberLeft(msg.sender);
    }

    function getMemberList() returns (address[]) {
        address[] memory list = new address[](members.length);

        for (uint i = 0; i<members.length; i++){
           list[i] = members[i].member;
        }
        return list;
    }

}