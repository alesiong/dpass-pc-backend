pragma solidity ^0.4.19;

contract Storage {
  address private owner;
  string[2][] public data;

  function Storage() public {
    owner = msg.sender;
  }

  function add(string key, string value) public {
    if (msg.sender == owner) {
      data.push([key, value]);
    }
  }

  function del(string key) public {
    if (msg.sender == owner) {
      data.push([key, ""]);
    }
  }
}
