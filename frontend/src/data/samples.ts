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

export const sampleSMSDump = `Rs.150.00 debited A/cXX6597 and credited to Vedamurthy M S via UPI Ref No 108589157513 on 17Nov25. Call 18001031906, if not done by you. -BOI
Rs.5500.00 credited in A/cXX6597 via NEFT Ref 894561235489 on 17Nov25. -BOI
Rs.899.00 debited from A/cXX6597 using UPI Ref 124578965412 on 18Nov25 at Myntra. -BOI
Rs.1200.00 debited from A/cXX6597 towards EMI on 19Nov25 Ref 785412369874 -BOI`

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


