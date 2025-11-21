# Data Files

This directory contains datasets and examples for the FairStake AI modules.

## Credit Scoring Datasets

### `realistic_fairscore_dataset.csv` (CURRENT MODEL)

- **Status**: ✅ Currently used for training FairScore model
- **Type**: Realistic synthetic data with income distribution patterns
- **Rows**: 1000
- **Generation**: `generate_realistic_dataset.py`
- **Features**:
  - Income distribution: 30% low (8-15k), 40% middle (15-30k), 20% upper-middle (30-60k), 10% high (60-100k)
  - Savings rate correlates with income (10-20% base)
  - Volatility inversely correlates with income (40% → 20%)
  - Context-aware EMI count and part-time income
  - Score range: 30-95 based on realistic weightage

### `synthetic_fairscore_dataset.csv` (LEGACY)

- **Status**: ⚠️ Legacy - uses purely random values
- **Type**: Basic synthetic data with random.randint/uniform
- **Rows**: 1000
- **Note**: Replaced by realistic dataset for better demo output

## SMS Parser Examples

### `real_sms_examples.txt`

- **Type**: Real SMS patterns from 18 Indian banks/wallets
- **Sources**: Axis, ICICI, HDFC, SBI, Kotak, Federal, IDFC, Canara, Paytm, Amazon Pay, PhonePe, Google Pay, Slice, Uni, HSBC, Citi, Lazypay, Simpl
- **Purpose**: Testing parser accuracy with actual bank SMS formats
- **Fields tested**: Amount, type, merchant, account, balance, bank, reference, date

### `synthetic_sms_examples.txt` (LEGACY)

- **Status**: ⚠️ Legacy - hand-written fake SMS
- **Type**: 10 simple synthetic SMS messages
- **Note**: Replaced by real_sms_examples.txt for testing

## Sample Documents

### `sample_loans/`

- `loan_fair_offer.txt` - Example of fair loan terms
- `loan_predatory_pack.txt` - Example of predatory loan document

### `sample_salary_slips/`

- `salary_slip_demo.txt` - Sample salary slip for Finance360 testing

### `sample_scheme_texts/`

- `scheme_gig_inclusive.txt` - Inclusive gig worker scheme
- `scheme_student_grant.txt` - Student grant scheme
- `scheme_urban_bias.txt` - Urban-biased scheme example

## Data Generation Scripts

### `generate_realistic_dataset.py`

- Generates `realistic_fairscore_dataset.csv` with realistic income distributions
- Uses statistical patterns matching Indian salary segments
- Creates context-aware features (savings, volatility, EMI, part-time income)

### `generate_fairscore_dataset.py` (LEGACY)

- Generates `synthetic_fairscore_dataset.csv` with random values
- Basic random number generation without realistic patterns

---

## Data Strategy

**Hybrid Approach**: We use a combination of:

1. **Realistic Synthetic Data** - For ML training (income-distribution-based, privacy-safe)
2. **Real SMS Patterns** - For parser testing and validation
3. **Sample Documents** - For legal AI and document processing demos

This ensures:

- ✅ Privacy protection (no actual user data)
- ✅ Realistic demo output quality
- ✅ Accurate ML model training
- ✅ Comprehensive testing coverage
