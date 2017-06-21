pragma solidity ^0.4.7;

import "OpenRegistry.sol";
import "Rules.sol";
import "BoardRoom.sol";
import "BaseProject.sol";

contract OpenRegistryRules is Rules {
  function OpenRegistryRules(address _registry) public {
    registry = OpenRegistry(_registry);
  }

  function hasWon(uint _proposalID) public constant returns (bool) {
    BoardRoom board = BoardRoom(msg.sender);

    uint nay = board.positionWeightOf(_proposalID, 0);
    uint yea = board.positionWeightOf(_proposalID, 1);
    uint totalVoters = board.numVoters(_proposalID);

    if(totalVoters > 0 && yea > nay) {
      return true;
    }
  }

  function canVote(address _sender, uint _proposalID) public constant returns (bool) {
    BoardRoom board = BoardRoom(msg.sender);

    uint created = board.createdOn(_proposalID);
    uint debatePeriod = board.debatePeriodOf(_proposalID);

    if(registry.memberId(_sender) > 0
      && now < created + debatePeriod
      && !board.hasVoted(_proposalID, _sender)) {
      return true;
    }
  }

  function canPropose(address _sender) public constant returns (bool) {
    if (registry.memberId(_sender) > 0) {
      return true;
    }
  }

  function canCreateProject(address _sender) public constant returns (bool) {
    if (registry.memberId(_sender) > 0) {
      return true;
    }    
  }


  function canPoll(address _project, address _sender) public constant returns (bool) {
    if (registry.memberIdForProject(_project, _sender) > 0) {
      return true;
    }
  }

  function canVoteInPoll(address _project, address _sender) public constant returns (bool) {
    if (registry.memberIdForProject(_project, _sender) > 0) {
      return true;
    }
  }

  function votingWeightOf(address _sender, uint _proposalID) public constant returns (uint) {
    address(_sender);
    uint(_proposalID);
    return 1;
  }

  OpenRegistry public registry;
}
