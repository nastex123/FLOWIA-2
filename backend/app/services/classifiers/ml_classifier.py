"""Classical Machine Learning document classifier using scikit-learn."""

from typing import Any, Dict, List, Optional
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
except ImportError:
    Pipeline = None  # type: ignore

from app.domain.schemas import ClassificationResult, DocumentType
from app.services.classifiers.base import BaseClassifier


# Default seed dataset for cold-start training of the classical ML model
SEED_TRAINING_DATA = [
    # INVOICE
    ("Factura número F-2024-001 emitida a Cliente SL con CIF B12345678 base imponible 1000 IVA 210 total 1210 EUR vencimiento", DocumentType.INVOICE),
    ("Tax invoice INV-8890 bill to TechCorp VAT ID GB99887766 subtotal 500 tax 100 total amount due 600 USD", DocumentType.INVOICE),
    ("Factura rectificativa abono importe total a pagar forma de pago transferencia bancaria fecha operacion", DocumentType.INVOICE),
    
    # PURCHASE_ORDER
    ("Orden de compra pedido de material PO-4500 proveedor suministros industriales fecha de entrega solicitada", DocumentType.PURCHASE_ORDER),
    ("Purchase order shipping address delivery date items requested item code quantity unit price total", DocumentType.PURCHASE_ORDER),
    ("Pedido de compra nº 9801 para aprovisionamiento de stock enviar a almacen central", DocumentType.PURCHASE_ORDER),
    
    # PAYROLL
    ("Recibo individual justificador del pago de salarios nómina periodo de liquidación salario base devengos deducciones irpf contingencias comunes líquido", DocumentType.PAYROLL),
    ("Payslip employee payroll gross pay net salary tax deductions social security contribution period", DocumentType.PAYROLL),
    ("Hoja de liquidación de haberes y sueldo mensual plus convenio retención irpf líquido total a percibir", DocumentType.PAYROLL),
    
    # INVENTORY
    ("Control de inventario stock actual referencia sku existencias unidades disponibles cantidad minima punto de reorden", DocumentType.INVENTORY),
    ("Warehouse inventory list item description sku in stock reserved units location bin rack quantity", DocumentType.INVENTORY),
    ("Listado de existencias en almacen valoración de inventario coste unitario total stock disponible", DocumentType.INVENTORY),
    
    # CONTRACT
    ("Contrato de prestación de servicios mercantiles reunidos de una parte y de otra comparecen acuerdan las siguientes estipulaciones y cláusulas", DocumentType.CONTRACT),
    ("Non disclosure agreement contract between parties hereby agree terms obligations confidential information termination clause", DocumentType.CONTRACT),
    ("Contrato de arrendamiento de local comercial fianza duración del contrato jurisdicción competente", DocumentType.CONTRACT),
    
    # FINANCIAL_REPORT
    ("Balance de situación ejercicio cerrado activo no corriente pasivo patrimonio neto cuenta de pérdidas y ganancias ebitda", DocumentType.FINANCIAL_REPORT),
    ("Financial statements annual report balance sheet cash flow statement income statement operating profit", DocumentType.FINANCIAL_REPORT),
]


class MLClassifier(BaseClassifier):
    """Supervised classical NLP classifier powered by TF-IDF and Logistic Regression."""

    def __init__(self, auto_train: bool = True):
        self.pipeline: Optional[Pipeline] = None
        self.is_trained: bool = False
        if auto_train and Pipeline is not None:
            self._train_default_model()

    def _train_default_model(self) -> None:
        """Trains the internal pipeline using the curated seed dataset."""
        texts = [item[0] for item in SEED_TRAINING_DATA]
        labels = [item[1].value for item in SEED_TRAINING_DATA]

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
            ("clf", LogisticRegression(C=1.0, max_iter=200, random_state=42)),
        ])
        self.pipeline.fit(texts, labels)
        self.is_trained = True

    def fit(self, texts: List[str], labels: List[DocumentType]) -> None:
        """Fits or updates the ML model with custom domain training data."""
        if Pipeline is None:
            raise RuntimeError("scikit-learn is not installed.")

        str_labels = [l.value if isinstance(l, DocumentType) else str(l) for l in labels]
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
            ("clf", LogisticRegression(C=1.0, max_iter=200, random_state=42)),
        ])
        self.pipeline.fit(texts, str_labels)
        self.is_trained = True

    def classify(
        self,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        if not text_content or not text_content.strip() or not self.is_trained or self.pipeline is None:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                classifier_type="scikit_learn_tfidf",
                matched_features=[],
            )

        # Predict probabilities
        probabilities = self.pipeline.predict_proba([text_content])[0]
        classes = self.pipeline.classes_

        best_idx = int(np.argmax(probabilities))
        best_class = classes[best_idx]
        confidence = float(probabilities[best_idx])

        # Get top matching n-grams from TF-IDF for explainability
        tfidf_step = self.pipeline.named_steps["tfidf"]
        feature_names = np.array(tfidf_step.get_feature_names_out())
        doc_vector = tfidf_step.transform([text_content]).toarray()[0]
        top_indices = np.argsort(doc_vector)[::-1][:5]
        top_features = [feature_names[idx] for idx in top_indices if doc_vector[idx] > 0]

        try:
            doc_type = DocumentType(best_class)
        except ValueError:
            doc_type = DocumentType.UNKNOWN

        return ClassificationResult(
            document_type=doc_type,
            confidence=round(confidence, 2),
            classifier_type="scikit_learn_tfidf",
            matched_features=top_features,
        )
