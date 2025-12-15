"""Field mapping and validation rules for hospital pharmacy data."""

from typing import Dict, Optional

# Field mappings based on sample data
FIELD_MAPPINGS = {
    'DOC': 'doc_id',
    'LINE': 'line_number',
    'CAT': 'drug_category',
    'C.R': 'consuming_dept',
    'DATE': 'transaction_date',
    'MOV #': 'movement_number',
    'MOV DES': 'movement_description',
    'CODE': 'drug_code',
    'ARTICLE': 'drug_name',
    'M': 'm_field',
    'C.S': 'supplying_dept',
    'QTY': 'quantity',
    'U.P': 'unit_price',
    'T.P': 'total_price',
    'AD DATE': 'admission_date',
    'R': 'room_number',
    'U': 'bed_number',
    'AGE': 'date_of_birth'  # Store as date of birth, not age
}

# Expected data types
EXPECTED_SCHEMA = {
    'DOC': 'int64',
    'LINE': 'int64',
    'CAT': 'int64',
    'C.R': 'int64',
    'DATE': 'str',  # Will be parsed to date
    'MOV #': 'int64',
    'MOV DES': 'str',
    'CODE': 'str',
    'ARTICLE': 'str',
    'M': 'str',
    'C.S': 'int64',
    'QTY': 'int64',
    'U.P': 'float64',
    'T.P': 'float64',
    'AD DATE': 'str',  # Will be parsed to date
    'R': 'int64',
    'U': 'int64',
    'AGE': 'str'
}

# Field descriptions (for documentation)
FIELD_DESCRIPTIONS = {
    'DOC': 'Document ID - unique identifier for the transaction record',
    'LINE': 'Line number - sequence within document',
    'CAT': 'Drug category code - classification by function/mechanism',
    'C.R': 'Consuming department - where drug was used',
    'DATE': 'Patient admission date (format: DD/MM/YY)',
    'MOV #': 'Unique movement transaction identifier',
    'MOV DES': 'Movement description in Arabic text',
    'CODE': 'Internal hospital drug code',
    'ARTICLE': 'Trade name of the drug',
    'M': 'Unknown field (requires investigation)',
    'C.S': 'Supplying department - source that issued the drug',
    'QTY': 'Quantity - negative = dispensed to patient, positive = received/stocked',
    'U.P': 'Unit price - cost per unit',
    'T.P': 'Total price - calculated as U.P × QTY',
    'AD DATE': 'Admission date (may duplicate DATE)',
    'R': 'Room number - patient\'s assigned hospital room',
    'U': 'Bed number - patient bed identifier',
    'AGE': 'Patient age (format may vary)'
}


def map_column_names(df, mappings: Dict = None) -> 'pl.DataFrame':
    """
    Map column names using field mappings.
    
    Args:
        df: Polars DataFrame
        mappings: Dictionary of column name mappings (defaults to FIELD_MAPPINGS)
    
    Returns:
        DataFrame with mapped column names
    """
    mappings = mappings or FIELD_MAPPINGS
    rename_dict = {old: new for old, new in mappings.items() if old in df.columns}
    
    if rename_dict:
        return df.rename(rename_dict)
    return df


def get_field_description(field_name: str) -> Optional[str]:
    """Get description for a field."""
    return FIELD_DESCRIPTIONS.get(field_name)


def get_all_field_descriptions() -> Dict[str, str]:
    """Get all field descriptions."""
    return FIELD_DESCRIPTIONS.copy()

