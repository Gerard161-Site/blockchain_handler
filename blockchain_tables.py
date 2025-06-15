from typing import List, Optional, Dict, Any
from mindsdb.integrations.libs.api_handler import APITable
from mindsdb.integrations.utilities.sql_utils import extract_comparison_conditions
from mindsdb_sql_parser.ast import Constant
import pandas as pd
import time


class BlocksTable(APITable):
    """Table for Bitcoin blocks data."""
    
    def get_columns(self) -> List[str]:
        return [
            'height', 'hash', 'time', 'main_chain', 'size', 'block_index',
            'received_time', 'relayed_by', 'n_tx', 'prev_block', 'mrkl_root',
            'version', 'bits', 'nonce'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Bitcoin blocks data."""
        conditions = extract_comparison_conditions(query.where)
        
        # Parse conditions
        block_hash = None
        block_height = None
        time_filter = None
        
        for op, arg1, arg2 in conditions:
            if arg1 == 'hash' and op == '=':
                block_hash = arg2
            elif arg1 == 'height' and op == '=':
                block_height = arg2
            elif arg1 == 'time' and op == '=':
                time_filter = arg2
        
        # Get data from API
        if block_hash:
            # Get specific block by hash
            response = self.handler.call_blockchain_api(f'/rawblock/{block_hash}')
            if response:
                return pd.DataFrame([self._process_block_data(response)], columns=self.get_columns())
        elif block_height:
            # Get block by height
            response = self.handler.call_blockchain_api(f'/block-height/{block_height}')
            if response and 'blocks' in response:
                rows = []
                for block in response['blocks']:
                    rows.append(self._process_block_data(block))
                return pd.DataFrame(rows, columns=self.get_columns())
        elif time_filter:
            # Get blocks for specific time (in milliseconds)
            response = self.handler.call_blockchain_api(f'/blocks/{time_filter}')
            if response and 'blocks' in response:
                rows = []
                for block in response['blocks']:
                    rows.append(self._process_block_summary(block))
                return pd.DataFrame(rows, columns=self.get_columns())
        else:
            # Get latest block
            response = self.handler.call_blockchain_api('/latestblock')
            if response:
                return pd.DataFrame([self._process_latest_block(response)], columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())
    
    def _process_block_data(self, block: Dict) -> List:
        """Process detailed block data."""
        return [
            block.get('height'),
            block.get('hash'),
            block.get('time'),
            block.get('main_chain'),
            block.get('size'),
            block.get('block_index'),
            block.get('received_time'),
            block.get('relayed_by'),
            block.get('n_tx'),
            block.get('prev_block'),
            block.get('mrkl_root'),
            block.get('ver'),
            block.get('bits'),
            block.get('nonce')
        ]
    
    def _process_block_summary(self, block: Dict) -> List:
        """Process block summary data from blocks endpoint."""
        return [
            block.get('height'),
            block.get('hash'),
            block.get('time'),
            True,  # main_chain default
            None,  # size not available in summary
            None,  # block_index not available
            None,  # received_time not available
            None,  # relayed_by not available
            None,  # n_tx not available
            None,  # prev_block not available
            None,  # mrkl_root not available
            None,  # version not available
            None,  # bits not available
            None   # nonce not available
        ]
    
    def _process_latest_block(self, block: Dict) -> List:
        """Process latest block data."""
        return [
            block.get('height'),
            block.get('hash'),
            block.get('time'),
            True,
            None,
            block.get('block_index'),
            None,
            None,
            len(block.get('txIndexes', [])),
            None,
            None,
            None,
            None,
            None
        ]


class TransactionsTable(APITable):
    """Table for Bitcoin transactions data."""
    
    def get_columns(self) -> List[str]:
        return [
            'hash', 'size', 'block_height', 'block_index', 'time', 'tx_index',
            'version', 'lock_time', 'vin_sz', 'vout_sz', 'fee', 'relayed_by',
            'inputs_count', 'outputs_count', 'total_input', 'total_output'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Bitcoin transactions data."""
        conditions = extract_comparison_conditions(query.where)
        
        # Parse conditions
        tx_hash = None
        
        for op, arg1, arg2 in conditions:
            if arg1 == 'hash' and op == '=':
                tx_hash = arg2
        
        if tx_hash:
            # Get specific transaction
            response = self.handler.call_blockchain_api(f'/rawtx/{tx_hash}')
            if response:
                return pd.DataFrame([self._process_transaction_data(response)], columns=self.get_columns())
        else:
            # Get unconfirmed transactions as default
            response = self.handler.call_blockchain_api('/unconfirmed-transactions')
            if response and 'txs' in response:
                rows = []
                for tx in response['txs'][:50]:  # Limit to 50 transactions
                    rows.append(self._process_transaction_data(tx))
                return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())
    
    def _process_transaction_data(self, tx: Dict) -> List:
        """Process transaction data."""
        inputs = tx.get('inputs', [])
        outputs = tx.get('out', [])
        
        total_input = sum(float(inp.get('prev_out', {}).get('value', 0)) for inp in inputs if inp.get('prev_out'))
        total_output = sum(float(out.get('value', 0)) for out in outputs)
        
        return [
            tx.get('hash'),
            tx.get('size'),
            tx.get('block_height'),
            tx.get('block_index'),
            tx.get('time'),
            tx.get('tx_index'),
            tx.get('ver'),
            tx.get('lock_time'),
            tx.get('vin_sz'),
            tx.get('vout_sz'),
            tx.get('fee'),
            tx.get('relayed_by'),
            len(inputs),
            len(outputs),
            total_input,
            total_output
        ]


class AddressesTable(APITable):
    """Table for Bitcoin address data."""
    
    def get_columns(self) -> List[str]:
        return [
            'address', 'hash160', 'n_tx', 'n_unredeemed', 'total_received',
            'total_sent', 'final_balance', 'first_tx_time', 'last_tx_time'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Bitcoin address data."""
        conditions = extract_comparison_conditions(query.where)
        
        # Parse conditions
        address = None
        addresses = []
        
        for op, arg1, arg2 in conditions:
            if arg1 == 'address':
                if op == '=':
                    address = arg2
                elif op == 'IN':
                    addresses = arg2 if isinstance(arg2, list) else [arg2]
        
        if address:
            # Get single address data
            response = self.handler.call_blockchain_api(f'/rawaddr/{address}')
            if response:
                return pd.DataFrame([self._process_address_data(response)], columns=self.get_columns())
        elif addresses:
            # Get multiple addresses data
            address_str = '|'.join(addresses)
            response = self.handler.call_blockchain_api(f'/multiaddr', {'active': address_str})
            if response and 'addresses' in response:
                rows = []
                for addr_data in response['addresses']:
                    rows.append(self._process_multiaddr_data(addr_data))
                return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())
    
    def _process_address_data(self, addr: Dict) -> List:
        """Process single address data."""
        transactions = addr.get('txs', [])
        first_tx_time = min(tx.get('time', float('inf')) for tx in transactions) if transactions else None
        last_tx_time = max(tx.get('time', 0) for tx in transactions) if transactions else None
        
        return [
            addr.get('address'),
            addr.get('hash160'),
            addr.get('n_tx'),
            addr.get('n_unredeemed'),
            addr.get('total_received'),
            addr.get('total_sent'),
            addr.get('final_balance'),
            first_tx_time if first_tx_time != float('inf') else None,
            last_tx_time if last_tx_time != 0 else None
        ]
    
    def _process_multiaddr_data(self, addr: Dict) -> List:
        """Process multi-address data."""
        return [
            addr.get('address'),
            addr.get('hash160'),
            addr.get('n_tx'),
            None,  # n_unredeemed not available in multiaddr
            addr.get('total_received'),
            addr.get('total_sent'),
            addr.get('final_balance'),
            None,  # first_tx_time not available
            None   # last_tx_time not available
        ]


class ChartsTable(APITable):
    """Table for Bitcoin charts and statistics data."""
    
    def get_columns(self) -> List[str]:
        return [
            'chart_type', 'timestamp', 'value', 'date'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Bitcoin charts data."""
        conditions = extract_comparison_conditions(query.where)
        
        # Parse conditions
        chart_type = 'market-price'  # Default chart type
        
        for op, arg1, arg2 in conditions:
            if arg1 == 'chart_type' and op == '=':
                chart_type = arg2
        
        # Get data from API
        response = self.handler.call_blockchain_api(f'/charts/{chart_type}', {'format': 'json'})
        
        if response and 'values' in response:
            rows = []
            for point in response['values']:
                rows.append([
                    chart_type,
                    point.get('x'),
                    point.get('y'),
                    time.strftime('%Y-%m-%d', time.gmtime(point.get('x', 0)))
                ])
            return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())


class StatsTable(APITable):
    """Table for Bitcoin network statistics."""
    
    def get_columns(self) -> List[str]:
        return [
            'market_price_usd', 'hash_rate', 'total_fees_btc', 'n_btc_mined',
            'n_tx', 'n_blocks_mined', 'minutes_between_blocks', 'totalbc',
            'n_blocks_total', 'estimated_transaction_volume_usd', 'blocks_size',
            'miners_revenue_usd', 'nextretarget', 'difficulty', 'estimated_btc_sent',
            'miners_revenue_btc', 'total_btc_sent', 'trade_volume_btc', 'trade_volume_usd',
            'timestamp'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get Bitcoin network statistics."""
        # Get data from API using stats endpoint
        response = self.handler.call_blockchain_api('/stats', {'format': 'json'})
        
        if response:
            current_time = int(time.time())
            row = [
                response.get('market_price_usd'),
                response.get('hash_rate'),
                response.get('total_fees_btc'),
                response.get('n_btc_mined'),
                response.get('n_tx'),
                response.get('n_blocks_mined'),
                response.get('minutes_between_blocks'),
                response.get('totalbc'),
                response.get('n_blocks_total'),
                response.get('estimated_transaction_volume_usd'),
                response.get('blocks_size'),
                response.get('miners_revenue_usd'),
                response.get('nextretarget'),
                response.get('difficulty'),
                response.get('estimated_btc_sent'),
                response.get('miners_revenue_btc'),
                response.get('total_btc_sent'),
                response.get('trade_volume_btc'),
                response.get('trade_volume_usd'),
                current_time
            ]
            return pd.DataFrame([row], columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns())


class UnconfirmedTransactionsTable(APITable):
    """Table for unconfirmed Bitcoin transactions."""
    
    def get_columns(self) -> List[str]:
        return [
            'hash', 'size', 'time', 'fee', 'inputs_count', 'outputs_count',
            'total_input_value', 'total_output_value', 'fee_per_byte'
        ]
    
    def select(self, query) -> pd.DataFrame:
        """Get unconfirmed Bitcoin transactions."""
        response = self.handler.call_blockchain_api('/unconfirmed-transactions', {'format': 'json'})
        
        if response and 'txs' in response:
            rows = []
            for tx in response['txs']:
                inputs = tx.get('inputs', [])
                outputs = tx.get('out', [])
                
                total_input = sum(float(inp.get('prev_out', {}).get('value', 0)) for inp in inputs if inp.get('prev_out'))
                total_output = sum(float(out.get('value', 0)) for out in outputs)
                
                fee = tx.get('fee', 0)
                size = tx.get('size', 1)
                fee_per_byte = fee / size if size > 0 else 0
                
                rows.append([
                    tx.get('hash'),
                    tx.get('size'),
                    tx.get('time'),
                    fee,
                    len(inputs),
                    len(outputs),
                    total_input,
                    total_output,
                    fee_per_byte
                ])
            return pd.DataFrame(rows, columns=self.get_columns())
        
        return pd.DataFrame(columns=self.get_columns()) 