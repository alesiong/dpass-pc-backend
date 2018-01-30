pragma solidity ^0.4.19;

// Make a factory contract to build each storage
contract Storage {
  address public owner;
  string[2][] public data;

  event Add(string key, string value);
  event Del(string key);

  function Storage() public {
    owner = msg.sender;
  }

  function add(string key, string value) public {
    if (msg.sender == owner) {
        data.push([key, value]);
        Add(key, value);
    }
  }

  function del(string key) public {
    if (msg.sender == owner) {
        data.push([key, ""]);
        Del(key);
    }
  }
}
