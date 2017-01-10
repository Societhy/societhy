pragma solidity ^0.4.7;

contract mortal {
    /* Define variable owner of the type address*/
    address owner;

    /* this function is executed at initialization and sets the owner of the contract */
    function mortal() { owner = msg.sender; }

    /* Function to recover the funds on the contract */
    function kill() { if (msg.sender == owner) selfdestruct(owner); }
}

contract greeter is mortal {
    /* define variable greeting of the type string */
    string greeting;
    address[] members;

    /* this runs when the contract is executed */
    function greeter(string _greeting) public {
        greeting = _greeting;

    }

    function join() public returns (string) {
        for (uint32 i = 0; i < members.length; i++) {
            if (msg.sender ==  members[i]) {
                throw ;
            }
        }
        members.push(msg.sender);
        return "OK";
    }

    function getMemberList() returns (address[]) {
        return members;
    }

    /* main function */
    function greet() constant returns (string) {
        return greeting;
    }
}