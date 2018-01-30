pragma solidity ^0.4.19;

// Make a factory contract to build each storage
contract Storage {
  address public owner;
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

  function del(string key) public {
    if (msg.sender == owner) {
        data.push([key, ""]);
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

    function del(string key) public {
        Storage s = Storage(storage_address[msg.sender]);
        s.del(key);
    }
}
