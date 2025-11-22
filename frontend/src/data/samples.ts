export const sampleSchemeText = `Applicants must submit 6 months salary slips and proof of employment from a metro city branch.
Scholarship is applicable only for male students residing in urban districts.
Processing fee of Rs. 500 is non-refundable.`

export const sampleSchemeResponse = {
  fairness_score: 62,
  clauses: [
    {
      id: 1,
      text: 'Applicants must submit 6 months salary slips and proof of employment from a metro city branch.',
      label: 'income_exclusion',
      confidence: 0.87,
      suggestion: 'Accept alternative proofs like bank inflows or gig statements.',
    },
    {
      id: 2,
      text: 'Scholarship is applicable only for male students residing in urban districts.',
      label: 'gender_bias',
      confidence: 0.9,
      suggestion: 'Ensure eligibility is gender-neutral and inclusive of rural regions.',
    },
  ],
  summary: 'Eligibility criteria favours salaried urban male applicants. Introduce alternative proofs and geographic inclusion.',
}

export const sampleSMSDump = `Rs.150.00 debited from A/c **1234 on 05-Feb-19 at 07:27:11. Avl Bal- Rs.2343.23. Not you? Call 1800111111 -Axis Bank
Rs.2000.00 debited from A/c no. XX3423 on 05-02-19 07:27:11 IST at ECS PAY. Avl Bal- INR 5343.23 -ICICI
INR 500.00 debited from A/c **4770 on 08-05-19 at Swiggy. Avl bal: INR 4843.23 -HDFC
Rs.1200 spent on Kotak Bank Credit Card XX1234 at AMAZON on 12-Nov-19. Avl limit: Rs.98765.00
Rs.250.00 added to your Paytm Wallet. Txn ID: 12345678. Balance: Rs.1500.00
Rs.299.00 paid via PhonePe to Zomato. UPI Ref: 987654321098. Balance: Rs.1201.00
You paid Rs.150.00 to Swiggy via Google Pay. UPI ID: merchant@okaxis. Ref: 123456789012
Rs.5000.00 debited from A/c XX6789 on 15-Nov-19. Info: NEFT-N123456789. Avl Bal: Rs.45678.90 -SBI
Rs.899.00 debited from Card XX1234 at MYNTRA on 18-Nov-19. Avl Credit Limit: Rs.87654.00 -Federal Bank
Rs.3500.00 credited to A/c XX4567 via IMPS. Ref: IDFCIMPS123456. Balance: Rs.49178.90 -IDFC
Rs.601.00 paid thru A/C XX4770 on 08-5-25 13:10:53 to AMAZON SELLER S, UPI Ref 284611545284 -Canara Bank`

export const sampleFairScoreFeatures = {
  avg_monthly_inflow: 12000,
  avg_monthly_outflow: 9000,
  savings_rate: 0.18,
  volatility: 0.22,
  part_time_income: 3500,
  academic_score: 8.6,
  emi_count: 1,
}

export const sampleLoanText = `The loan will auto-renew every 3 months unless cancelled in writing.
APR is 38% with a processing fee of 6% deducted upfront.
Mandatory insurance bundled with loan disbursement.`


