"""Shared, deterministic train/validation/test split and classification metrics."""
from pathlib import Path
import hashlib
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent

def dataset_splits():
    df = pd.read_csv(HERE / 'telco_churn.csv')
    if not df.customerID.is_unique or df.isna().any().any():
        raise ValueError('Expected unique customer IDs and complete input rows')
    if not set(df.Churn).issubset({'Yes', 'No'}):
        raise ValueError('Unexpected target label')
    trainval, test = train_test_split(df, test_size=.2, stratify=df.Churn, random_state=42)
    train, validation = train_test_split(trainval, test_size=.25, stratify=trainval.Churn, random_state=42)
    return {'train': train, 'validation': validation, 'test': test}

def features(frame):
    return frame.drop(columns=['customerID', 'Churn'])

def target(frame):
    return (frame.Churn == 'Yes').astype(int)

def score(y, probabilities, threshold):
    pred = (probabilities >= threshold).astype(int)
    return {'threshold': float(threshold), 'accuracy': float(accuracy_score(y, pred)),
            'precision': float(precision_score(y, pred, zero_division=0)),
            'recall': float(recall_score(y, pred, zero_division=0)),
            'f1': float(f1_score(y, pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y, probabilities)),
            'average_precision': float(average_precision_score(y, probabilities))}

def data_hash():
    return hashlib.sha256((HERE / 'telco_churn.csv').read_bytes()).hexdigest()
