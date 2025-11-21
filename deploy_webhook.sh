#!/bin/bash

# Deploy Ko‑fi webhook to Google Cloud Functions (2nd Gen)
# Usage: ./deploy_webhook.sh <GCP_PROJECT_ID>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$1" ]; then
  echo -e "${RED}❌ Project ID argument missing${NC}"
  echo "Usage: $0 <GCP_PROJECT_ID>"
  exit 1
fi

PROJECT_ID="$1"
FUNCTION_NAME="kofi-handler"
REGION="us-central1"
TOKEN_FILE=".kofi_token"

# Generate verification token
KOFI_TOKEN=$(openssl rand -hex 16)

echo "$KOFI_TOKEN" > "$TOKEN_FILE"

echo -e "${GREEN}✓${NC} Verification token saved to ${YELLOW}$TOKEN_FILE${NC}"

# Deploy function

gcloud functions deploy "$FUNCTION_NAME" \
  --gen2 \
  --runtime=python311 \
  --region="$REGION" \
  --source=./webhook_service \
  --entry-point=kofi_handler \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=KOFI_VERIFICATION_TOKEN=$KOFI_TOKEN \
  --project="$PROJECT_ID" \
  --memory=256MB \
  --timeout=60s

# Get function URL
FUNCTION_URL=$(gcloud functions describe "$FUNCTION_NAME" \
  --gen2 \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(serviceConfig.uri)")

echo -e "\n${BLUE}=== Deployment Complete ===${NC}"
echo -e "${YELLOW}Function URL:${NC} $FUNCTION_URL"
echo -e "${YELLOW}Ko‑fi Verification Token:${NC} $KOFI_TOKEN"

# Make script executable (in case it wasn't)
chmod +x "$0"
