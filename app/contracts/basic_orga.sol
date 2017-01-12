pragma solidity ^0.4.7;

contract mortal {
    /* Define variable owner of the type address*/
    address owner;

    /* this function is executed at initialization and sets the owner of the contract */
    function mortal() { owner = msg.sender; }

    /* Function to recover the funds on the contract */
    function kill() { if (msg.sender == owner) selfdestruct(owner); }
}

contract basic_orga is mortal {
    /* define variable greeting of the type string */
    string name;
    address[] members;
    
    event newMember(address orga, address member);
    event memberLeft(address orga, address member);

    /* this runs when the contract is executed */
    function basic_orga(string _name) public {
        name = _name;

    }

    function join() public {
        for (uint32 i = 0; i < members.length; i++) {
            if (msg.sender ==  members[i]) {
                throw ;
            }
        }
        members.push(msg.sender);
        newMember(this, msg.sender);
        return "OK";
    }

    function leave() /* modifier */{
        
    }

    function donate() public returns (string) {

    }

    function getMemberList() returns (address[]) {
        return members;
    }

    /* main function */
    function getName() constant returns (string) {
        return name;
    }
}