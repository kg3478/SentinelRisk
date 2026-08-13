# SentinelRisk — System Limitations & Disclaimer

## Scope & Data Limitations

1. **Research Dataset Context**: SentinelRisk is trained on the MLG-ULB Credit Card Fraud Detection benchmark dataset (anonymized PCA features V1-V28). It does not use live streaming banking data.
2. **Delayed Fraud Labels**: Fraud labels in real-world card networks often arrive with a 30-90 day chargeback delay. SentinelRisk assumes historical ground-truth labels for evaluation partitions.
3. **Synthetic Sandbox Fixtures**: The live authorization sandbox includes synthetic test scenarios labeled explicitly as `SYNTHETIC TEST FIXTURE` for demonstration purposes.
