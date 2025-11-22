# AWS Bedrock RAG Setup Guide

This guide walks you through setting up **AWS Bedrock Knowledge Base** for the Contract Q&A feature. By the end, you'll have AI-powered contract analysis with citations.

---

## What You're Building

```
Contract PDFs → S3 Bucket → Bedrock Knowledge Base → Vector Search
                                      ↓
                            Claude AI generates answer
                                      ↓
                            Frontend shows: Answer + Citations
```

**Cost estimate**: ~$5-20/month for development (pay-per-use, no upfront costs)

---

## Prerequisites

✅ AWS Account with billing enabled  
✅ AWS CLI installed (optional but recommended)  
✅ Sample contract PDFs (MSA, NDA, Terms of Service, etc.)  
✅ Basic understanding of S3 and IAM

---

## Step 1: Create S3 Bucket for Contracts

**Why**: S3 stores your contract PDFs. Bedrock reads from here.

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click **Create bucket**
3. Settings:
   - **Bucket name**: `fairstake-rag-data` (must be globally unique; add your initials if taken)
   - **Region**: `us-east-1` (or your preferred region)
   - **Block all public access**: ✅ Keep enabled (default)
   - Leave other settings as default
4. Click **Create bucket**
5. Click your new bucket → Click **Create folder**
   - **Folder name**: `contracts/`
   - Click **Create folder**

**What success looks like**:

- You see `fairstake-rag-data` in your bucket list
- Inside it, a `contracts/` folder exists

---

## Step 2: Upload Sample Contract PDFs

**Why**: Bedrock needs documents to search through.

1. In S3, navigate to `fairstake-rag-data/contracts/`
2. Click **Upload**
3. Click **Add files**
4. Select 2-5 contract PDFs (examples: MSA, NDA, SaaS agreement)
   - **Tip**: Use text-based PDFs (not scanned images). If scanned, use AWS Textract or online OCR first.
5. Click **Upload**
6. Wait for "Upload succeeded" message

**What success looks like**:

```
fairstake-rag-data/
  └─ contracts/
      ├─ MSA_sample.pdf
      ├─ NDA_template.pdf
      └─ SaaS_terms.pdf
```

---

## Step 3: Request Bedrock Model Access

**Why**: AWS requires explicit approval to use Claude models (security measure).

1. Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Left sidebar → **Model access**
3. Click **Edit** (top right)
4. Find **Anthropic** section
5. Check these models:
   - ✅ Claude 3.5 Sonnet v2
   - ✅ Claude 3 Haiku (optional, cheaper fallback)
6. Check **Amazon** section:
   - ✅ Titan Embeddings G1 - Text
7. Click **Request model access**
8. Wait 1-5 minutes (usually instant for Titan; Claude may take hours)

**What success looks like**:

- Status shows **Access granted** (green) for all models
- If "Pending", check back in 1 hour or use local fallback

---

## Step 4: Create IAM Role for Bedrock

**Why**: Bedrock needs permission to read your S3 bucket.

### Option A: Console (Beginner-friendly)

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Left sidebar → **Roles** → **Create role**
3. **Trusted entity type**: AWS service
4. **Use case**: Bedrock → **Bedrock - Knowledge Base** → **Next**
5. **Permissions**: Click **Create policy** (opens new tab)
6. In new tab:
   - Click **JSON** tab
   - Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadContracts",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::fairstake-rag-data",
        "arn:aws:s3:::fairstake-rag-data/*"
      ]
    },
    {
      "Sid": "BedrockModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

7. Click **Next**
8. **Policy name**: `FairStake-Bedrock-KB-Policy`
9. Click **Create policy**
10. Go back to role creation tab → Refresh policies → Select `FairStake-Bedrock-KB-Policy`
11. Click **Next**
12. **Role name**: `FairStake-Bedrock-KB-Role`
13. Click **Create role**
14. **Copy the Role ARN** (looks like `arn:aws:iam::123456789012:role/FairStake-Bedrock-KB-Role`)

**What success looks like**:

- Role appears in IAM Roles list
- Policy is attached
- Role ARN is saved in your notes

---

## Step 5: Create Bedrock Knowledge Base

**Why**: This indexes your PDFs and enables semantic search.

1. Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Left sidebar → **Knowledge bases** → **Create knowledge base**

### Basic Info

3. **Knowledge base name**: `fairstake-contracts-kb`
4. **IAM role**: Select **Choose an existing service role** → Select `FairStake-Bedrock-KB-Role`
5. Click **Next**

### Data Source

6. **Data source name**: `S3-Contracts`
7. **S3 URI**: Browse → Select `fairstake-rag-data/contracts/`
   - Should show: `s3://fairstake-rag-data/contracts/`
8. Click **Next**

### Embeddings Model

9. **Embeddings model**: Amazon Titan Embeddings G1 - Text
10. **Vector database**: Quick create a new vector store (recommended)
    - This auto-creates OpenSearch Serverless for you
    - **Collection name**: `fairstake-kb-collection` (auto-filled)
11. Click **Next**

### Review

12. Review settings → Click **Create knowledge base**

**Wait time**: 3-10 minutes (creating vector store, ingesting documents)

**What success looks like**:

- Status shows **ACTIVE** (green)
- Data source shows **Available**
- You see a **Knowledge Base ID** like `kb-abc123def456ghi789`

---

## Step 6: Sync Data Source

**Why**: This processes PDFs → creates embeddings → stores in vector DB.

1. Still in Knowledge Base detail page
2. Click **Data sources** tab
3. Select `S3-Contracts`
4. Click **Sync** button (top right)
5. Wait 2-5 minutes for sync to complete

**What success looks like**:

- Sync status: **Succeeded** (green checkmark)
- **Documents**: Shows number of PDFs processed (e.g., "3 documents")
- **Last sync time**: Just now

**Common issue**: "Failed to sync"

- **Fix**: Check IAM role has S3 read permission
- **Fix**: Ensure PDFs are text-based (not scanned images)

---

## Step 7: Get Knowledge Base ID

**Why**: Backend needs this to query the KB.

1. In Knowledge Base detail page, look at top section
2. Find **Knowledge Base ID**: Looks like `kb-abc123def456ghi789`
3. Click **Copy** icon
4. Open `backend/.env` in VS Code
5. Paste into `KNOWLEDGE_BASE_ID=` line:

```env
KNOWLEDGE_BASE_ID=kb-abc123def456ghi789
```

6. Save file
7. Restart backend: `Ctrl+C` in terminal running `start_backend.ps1`, then run again

**What success looks like**:

```bash
# Test health endpoint
curl http://localhost:8000/api/rag-health
# Should return: {"configured": true, "knowledge_base_id": "kb-abc1..."}
```

---

## Step 8: Configure AWS Credentials

**Why**: Backend needs permission to call Bedrock API.

### Option A: Local Development (aws configure)

```powershell
# Install AWS CLI: https://aws.amazon.com/cli/
aws configure
# Enter:
AWS Access Key ID: [Your access key]
AWS Secret Access Key: [Your secret key]
Default region name: us-east-1
Default output format: json
```

### Option B: IAM Role (Production - App Runner/EC2)

1. When deploying to AWS, attach IAM role to service
2. Role should have this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:RetrieveAndGenerate",
        "bedrock:Retrieve",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::fairstake-rag-data/*"
    }
  ]
}
```

**Security note**: Never commit AWS keys to Git. Use environment variables or IAM roles.

---

## Step 9: Test the Integration

1. Start backend: `.\start_backend.ps1`
2. Start frontend: `.\start_frontend.ps1`
3. Open http://localhost:5173
4. Click **Contract Q&A** tab
5. Try a sample question: "What are the termination penalties?"
6. Click **Search Knowledge Base**

**What success looks like**:

- Answer appears (3-10 seconds)
- Citations show with document name, page, and snippet
- No error messages

**Common issues**:

| Error                              | Fix                                              |
| ---------------------------------- | ------------------------------------------------ |
| "KNOWLEDGE_BASE_ID not configured" | Check `.env` file saved correctly                |
| "AWS access denied"                | Run `aws configure` with valid credentials       |
| "ResourceNotFoundException"        | Check KB ID is correct, region matches           |
| "Model access denied"              | Request model access in Bedrock console (Step 3) |
| Empty citations                    | Re-sync data source, check PDFs are text-based   |

---

## Step 10: Re-sync After Adding PDFs

**When**: Every time you upload new contracts to S3.

1. Go to Bedrock console → Knowledge bases → `fairstake-contracts-kb`
2. Data sources tab → Select `S3-Contracts`
3. Click **Sync**
4. Wait for "Succeeded" status

**Why**: Knowledge Base doesn't auto-detect new files; manual sync required.

---

## Cost Breakdown

| Service               | Cost                   | Usage                  |
| --------------------- | ---------------------- | ---------------------- |
| S3 storage            | $0.023/GB/month        | ~$0.10 for 100 PDFs    |
| Bedrock embeddings    | $0.0001/1k tokens      | ~$0.50 for 1k pages    |
| Claude 3.5 Sonnet     | $0.003/1k input tokens | ~$1-5 for 100 queries  |
| OpenSearch Serverless | ~$8-10/month           | Fixed cost (OCU-based) |

**Total**: ~$10-15/month for light development use.

**Tip**: Delete Knowledge Base when not in use to save OpenSearch costs.

---

## Troubleshooting

### ❌ "Cannot import name 'bedrock-agent-runtime'"

**Fix**: Update boto3:

```powershell
pip install boto3 --upgrade
```

### ❌ Citations always empty

**Causes**:

1. PDFs are scanned images (no extractable text)
   - **Fix**: Use OCR (AWS Textract or online tools)
2. Data source not synced
   - **Fix**: Sync in Bedrock console
3. Query too vague
   - **Fix**: Ask specific questions: "What is the notice period for termination?"

### ❌ "Region mismatch"

**Fix**: Ensure all services in same region:

- S3 bucket: `us-east-1`
- Knowledge Base: `us-east-1`
- `.env` `AWS_REGION=us-east-1`

### ❌ Slow responses (>30 seconds)

**Causes**:

1. First query after sync (cold start)
   - **Fix**: Normal; subsequent queries faster
2. Large PDFs (100+ pages)
   - **Fix**: Split into smaller files

---

## Next Steps

1. **Add more contracts**: Upload to S3, re-sync KB
2. **Tune prompts**: Edit `promptTemplate` in `backend/app/routes/rag.py`
3. **Add re-ranking**: Implement semantic similarity scoring before Claude
4. **Feedback loop**: Store thumbs-up/down in DynamoDB for model improvement
5. **Deploy to production**: Use AWS App Runner with IAM role (no hardcoded keys)

---

## Resources

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Knowledge Base User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Claude 3.5 Sonnet Docs](https://docs.anthropic.com/claude/docs)
- [Boto3 Bedrock Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html)

---

## Security Checklist

- [ ] S3 bucket has Block Public Access enabled
- [ ] IAM policies follow least privilege (no `s3:*` or `bedrock:*`)
- [ ] AWS credentials not committed to Git (check `.gitignore`)
- [ ] Production uses IAM roles (not access keys)
- [ ] Knowledge Base ID in `.env` (not hardcoded)
- [ ] Rotate IAM access keys quarterly
- [ ] Enable CloudWatch logging for audit trail

---

**Need help?** Open an issue with:

1. Error message (from browser console or backend logs)
2. Output of `curl http://localhost:8000/api/rag-health`
3. AWS region and Knowledge Base ID (first 10 chars only)
