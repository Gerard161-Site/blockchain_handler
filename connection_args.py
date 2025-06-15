connection_args = {
    'base_url': {
        'type': 'str',
        'description': 'Blockchain.com API base URL',
        'default': 'https://blockchain.info'
    },
    'cors': {
        'type': 'bool',
        'description': 'Enable CORS headers',
        'default': True
    }
}

connection_args_example = {
    'base_url': 'https://blockchain.info',
    'cors': True
} 