from chain.control.main import parse_config, main

if __name__ == '__main__':
    config = parse_config()
    main(config)
