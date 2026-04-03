---
name: scikit-learn
description: "Classical machine learning in Python -- classification, regression, clustering, and pipelines."
---

# Scikit-learn

Industry-standard Python library for classical machine learning. Provides consistent API across classification, regression, clustering, dimensionality reduction, preprocessing, and model evaluation. Use for tabular/structured data where interpretable ML or rapid prototyping is needed.

## Key Patterns

- **Always use Pipelines**: Chain preprocessing + model to prevent data leakage during cross-validation
- **Fit on train only**: `scaler.fit_transform(X_train)` then `scaler.transform(X_test)` -- never fit on test
- **Stratified splits**: `train_test_split(X, y, stratify=y)` for classification to preserve class distribution
- **ColumnTransformer for mixed types**: Apply `StandardScaler` to numeric, `OneHotEncoder` to categorical in one step
- **Scale when required**: SVM, KNN, Neural Nets, PCA, regularized linear models need scaling; tree-based models do not
- **Hyperparameter tuning**: `GridSearchCV` for small spaces, `RandomizedSearchCV` for large; always use cross-validation
- **Imbalanced data**: Use precision/recall/ROC-AUC instead of accuracy; consider `class_weight='balanced'`
- **Set random_state**: For reproducibility in models, splits, and search
- **Feature selection**: `SelectKBest`, `RFE`, or `SelectFromModel` to reduce dimensionality
- **ConvergenceWarning fix**: Increase `max_iter` or scale features

## Quick Reference

### Algorithm Selection

| Task | Start With | Alternatives |
|:-----|:-----------|:-------------|
| Classification (balanced) | RandomForest | GradientBoosting, LogisticRegression |
| Classification (imbalanced) | GradientBoosting + class_weight | SVM, balanced sampling |
| Regression | GradientBoosting | Ridge, RandomForest, SVR |
| Clustering | KMeans | DBSCAN (arbitrary shape), GMM (probabilistic) |
| Dimensionality reduction | PCA | t-SNE (viz), UMAP (viz + structure) |
| Feature selection | SelectFromModel | RFE, SelectKBest |
| Large dataset | SGDClassifier/Regressor | MiniBatchKMeans |

### Core Pipeline Pattern

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

# Preprocessing
preprocessor = ColumnTransformer([
    ('num', Pipeline([('imp', SimpleImputer(strategy='median')),
                      ('scl', StandardScaler())]), numeric_cols),
    ('cat', Pipeline([('imp', SimpleImputer(strategy='most_frequent')),
                      ('ohe', OneHotEncoder(handle_unknown='ignore'))]), cat_cols)
])

# Full pipeline
model = Pipeline([('prep', preprocessor),
                  ('clf', RandomForestClassifier(random_state=42))])

# Tune and evaluate
grid = GridSearchCV(model, {'clf__n_estimators': [100, 200],
                            'clf__max_depth': [10, 20, None]}, cv=5)
grid.fit(X_train, y_train)
print(classification_report(y_test, grid.predict(X_test)))
```

### Clustering Pattern

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

X_scaled = StandardScaler().fit_transform(X)
scores = [silhouette_score(X_scaled, KMeans(n_clusters=k, random_state=42).fit_predict(X_scaled))
          for k in range(2, 11)]
optimal_k = range(2, 11)[np.argmax(scores)]

labels = KMeans(n_clusters=optimal_k, random_state=42).fit_predict(X_scaled)
X_2d = PCA(n_components=2).fit_transform(X_scaled)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis')
```

### Common Fixes

- **ConvergenceWarning**: `LogisticRegression(max_iter=1000)` or scale features
- **Overfitting**: Add regularization (`Ridge(alpha=1.0)`), use cross-validation, simplify model
- **Memory error**: Use `SGDClassifier` or `MiniBatchKMeans` for large datasets

## When to Use

- Building classification or regression models on tabular data
- Performing clustering (KMeans, DBSCAN) or dimensionality reduction (PCA, t-SNE)
- Creating reproducible ML pipelines with preprocessing, tuning, and evaluation
- Comparing multiple algorithms quickly with consistent API
- Need interpretable, classical ML rather than deep learning

## Resources

- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Algorithm Cheat Sheet](https://scikit-learn.org/stable/tutorial/machine_learning_map/)
