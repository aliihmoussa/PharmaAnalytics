"""STORE file column mappings (Excel sheet rep25071808450909)."""

# Source column -> canonical/DB column
INVENTORY_FIELD_MAPPINGS = {
    'DOC': 'doc_id',
    'LINE': 'line_number',
    'CAT': 'cat',
    'C.R': 'cr',
    'DATE': 'transaction_date',
    'MOV': 'movement_number',
    'MOV DES': 'movement_description',
    'CODE': 'drug_code',
    'ARTICLE': 'drug_name',
    'M': 'm_field',
    'C.S': 'cs',
    'QTY': 'quantity',
    'U.P': 'unit_price',
    'T.P': 'total_price',
    'VOICHER': 'voucher',
}

# STORE data sheet name (second sheet in STORE 2024.xlsx)
STORE_DATA_SHEET = 'rep25071808450909'
