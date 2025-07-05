import requests
from typing import Optional, Dict, Any
from mindsdb.integrations.libs.api_handler import APIHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE
)
from mindsdb.utilities import log
from mindsdb_sql_parser import parse_sql
from .blockchain_tables import (
    BlocksTable,
    TransactionsTable,
    AddressesTable,
    ChartsTable,
    StatsTable,
    UnconfirmedTransactionsTable
)

logger = log.getLogger(__name__)


class BlockchainHandler(APIHandler):
    """
    The Blockchain.com handler implementation.
    """
    
    name = 'blockchain'
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize the Blockchain.com handler.
        
        Args:
            name (str): The handler name
            kwargs: Connection arguments
        """
        super().__init__(name)
        
        # Connection parameters
        connection_data = kwargs.get('connection_data', {})
        self.base_url = connection_data.get('base_url', 'https://blockchain.info')
        self.cors = connection_data.get('cors', True)
        
        # API configuration
        self.headers = {
            'User-Agent': 'MindsDB-Blockchain-Handler/1.0',
            'Accept': 'application/json'
        }
        
        # Register available tables
        self._register_table('blocks', BlocksTable(self))
        self._register_table('transactions', TransactionsTable(self))
        self._register_table('addresses', AddressesTable(self))
        self._register_table('charts', ChartsTable(self))
        self._register_table('stats', StatsTable(self))
        self._register_table('unconfirmed_transactions', UnconfirmedTransactionsTable(self))
        
    def connect(self) -> StatusResponse:
        """
        Set up any connections required by the handler.
        
        Returns:
            HandlerStatusResponse
        """
        try:
            # Test connection by getting latest block
            response = self.call_blockchain_api('/latestblock')
            if response and 'hash' in response:
                self.is_connected = True
                return StatusResponse(True)
            else:
                self.is_connected = False
                return StatusResponse(False, "Connection failed: Invalid response from Blockchain.com API")
        except Exception as e:
            self.is_connected = False
            logger.error(f"Error connecting to Blockchain.com: {e}")
            return StatusResponse(False, f"Connection failed: {str(e)}")
    
    def check_connection(self) -> StatusResponse:
        """
        Check if the connection is alive and healthy.
        
        Returns:
            HandlerStatusResponse
        """
        return self.connect()
    
    def native_query(self, query: str) -> Response:
        """
        Receive and process a raw query.
        
        Args:
            query (str): query in native format
            
        Returns:
            HandlerResponse
        """
        ast = parse_sql(query, dialect='mindsdb')
        return self.query(ast)
    
    def call_blockchain_api(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Call Blockchain.com API endpoint.
        
        Args:
            endpoint (str): API endpoint path
            params (dict): Optional query parameters
            
        Returns:
            API response data
        """
        # FIXED: Charts endpoints need api.blockchain.info instead of blockchain.info
        if endpoint.startswith('/charts/'):
            base_url = 'https://api.blockchain.info'
        else:
            base_url = self.base_url
            
        url = base_url + endpoint
        
        # Add CORS parameter if enabled
        if self.cors:
            if params is None:
                params = {}
            params['cors'] = 'true'
        
        try:
            response = requests.get(url, headers=self.headers, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            raise 