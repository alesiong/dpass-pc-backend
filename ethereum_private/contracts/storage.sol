pragma solidity ^0.4.19;

// Make a factory contract to build each storage
contract Storage {
  address private owner;
  string[2][] public data;
  uint public length;

  function Storage() public {
    owner = msg.sender;
  }

  function add(string key, string value) public {
    if (msg.sender == owner) {
        data.push([key, value]);
        length++;
    }
  }
}

contract StorageFactory {
    mapping(address => address) public storage_address;
    function new_storage() public {
        Storage s = new Storage();
        if (storage_address[msg.sender] == address(0x0))
            storage_address[msg.sender] = s;
    }

    function add(string key, string value) public {
        Storage s = Storage(storage_address[msg.sender]);
        s.add(key, value);
    }
}
