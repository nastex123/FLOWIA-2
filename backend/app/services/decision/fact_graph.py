"""Fact Graph Engine using NetworkX for transactional relationship reasoning and 3-way matching."""

from typing import Any, Dict, List, Optional
import networkx as nx


class FactGraphEngine:
    """Relational transactional graph connecting projects, orders, deliveries, invoices and payments."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_project(self, project_id: str, name: str, budget: float) -> None:
        self.graph.add_node(
            f"project:{project_id}",
            type="project",
            id=project_id,
            name=name,
            budget=budget,
        )

    def add_vendor(self, vendor_id: str, name: str, tax_id: str) -> None:
        self.graph.add_node(
            f"vendor:{vendor_id}",
            type="vendor",
            id=vendor_id,
            name=name,
            tax_id=tax_id,
        )

    def add_purchase_order(
        self,
        po_id: str,
        po_number: str,
        vendor_id: str,
        total_amount: float,
        project_id: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        po_node = f"po:{po_id}"
        self.graph.add_node(
            po_node,
            type="purchase_order",
            id=po_id,
            po_number=po_number,
            total_amount=total_amount,
            items=items or [],
        )

        vendor_node = f"vendor:{vendor_id}"
        if vendor_node in self.graph:
            self.graph.add_edge(po_node, vendor_node, relation="ORDERED_FROM")

        if project_id:
            project_node = f"project:{project_id}"
            if project_node in self.graph:
                self.graph.add_edge(project_node, po_node, relation="HAS_PO")

    def add_goods_receipt(
        self,
        gr_id: str,
        gr_number: str,
        po_id: str,
        items: Optional[List[Dict[str, Any]]] = None,
        received_date: Optional[str] = None,
    ) -> None:
        gr_node = f"gr:{gr_id}"
        self.graph.add_node(
            gr_node,
            type="goods_receipt",
            id=gr_id,
            gr_number=gr_number,
            received_date=received_date,
            items=items or [],
        )

        po_node = f"po:{po_id}"
        if po_node in self.graph:
            self.graph.add_edge(gr_node, po_node, relation="FULFILLS")

    def add_invoice(
        self,
        invoice_id: str,
        invoice_number: str,
        vendor_id: str,
        total_amount: float,
        po_id: Optional[str] = None,
        gr_id: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        inv_node = f"invoice:{invoice_id}"
        self.graph.add_node(
            inv_node,
            type="invoice",
            id=invoice_id,
            invoice_number=invoice_number,
            total_amount=total_amount,
            items=items or [],
        )

        vendor_node = f"vendor:{vendor_id}"
        if vendor_node in self.graph:
            self.graph.add_edge(inv_node, vendor_node, relation="ISSUED_BY")

        if po_id:
            po_node = f"po:{po_id}"
            if po_node in self.graph:
                self.graph.add_edge(inv_node, po_node, relation="REFERENCES_PO")

        if gr_id:
            gr_node = f"gr:{gr_id}"
            if gr_node in self.graph:
                self.graph.add_edge(inv_node, gr_node, relation="CLAIMS_PAYMENT_FOR")

    def add_payment(
        self,
        payment_id: str,
        invoice_id: str,
        amount: float,
        paid_at: str,
        bank_account: Optional[str] = None,
    ) -> None:
        pay_node = f"payment:{payment_id}"
        self.graph.add_node(
            pay_node,
            type="payment",
            id=payment_id,
            amount=amount,
            paid_at=paid_at,
            bank_account=bank_account,
        )

        inv_node = f"invoice:{invoice_id}"
        if inv_node in self.graph:
            self.graph.add_edge(pay_node, inv_node, relation="SETTLES")

    def get_po_invoiced_total(self, po_id: str) -> float:
        """Calculates the cumulative invoiced total across all invoices referencing a Purchase Order."""
        po_node = f"po:{po_id}"
        if po_node not in self.graph:
            return 0.0

        total_invoiced = 0.0
        for predecessor in self.graph.predecessors(po_node):
            node_data = self.graph.nodes[predecessor]
            if node_data.get("type") == "invoice":
                total_invoiced += node_data.get("total_amount", 0.0)

        return round(total_invoiced, 2)

    def check_overbilling(self, po_id: str) -> Dict[str, Any]:
        """Checks if the cumulative invoiced amount exceeds the authorized PO budget."""
        po_node = f"po:{po_id}"
        if po_node not in self.graph:
            return {"error": "Purchase order not found"}

        po_budget = self.graph.nodes[po_node].get("total_amount", 0.0)
        total_invoiced = self.get_po_invoiced_total(po_id)
        is_overbilled = total_invoiced > po_budget
        deviation = round(total_invoiced - po_budget, 2) if is_overbilled else 0.0

        return {
            "po_id": po_id,
            "po_budget": po_budget,
            "total_invoiced": total_invoiced,
            "is_overbilled": is_overbilled,
            "overbilled_amount": deviation,
        }

    def find_orphan_invoices(self) -> List[str]:
        """Finds invoices that have no associated Purchase Order (unauthorized billing)."""
        orphans = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "invoice":
                # Check if it has an outgoing edge to a PO
                has_po = any(
                    self.graph.nodes[target].get("type") == "purchase_order"
                    for target in self.graph.successors(node)
                )
                if not has_po:
                    orphans.append(data.get("id"))
        return orphans

    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Computes total project budget vs committed POs vs invoiced vs paid."""
        proj_node = f"project:{project_id}"
        if proj_node not in self.graph:
            return {"error": "Project not found"}

        budget = self.graph.nodes[proj_node].get("budget", 0.0)
        total_po = 0.0
        total_invoiced = 0.0
        total_paid = 0.0

        # POs under project
        for po_target in self.graph.successors(proj_node):
            po_data = self.graph.nodes[po_target]
            if po_data.get("type") == "purchase_order":
                total_po += po_data.get("total_amount", 0.0)
                # Invoices under this PO
                for inv_source in self.graph.predecessors(po_target):
                    inv_data = self.graph.nodes[inv_source]
                    if inv_data.get("type") == "invoice":
                        total_invoiced += inv_data.get("total_amount", 0.0)
                        # Payments under this invoice
                        for pay_source in self.graph.predecessors(inv_source):
                            pay_data = self.graph.nodes[pay_source]
                            if pay_data.get("type") == "payment":
                                total_paid += pay_data.get("amount", 0.0)

        return {
            "project_id": project_id,
            "budget": budget,
            "committed_po_total": round(total_po, 2),
            "invoiced_total": round(total_invoiced, 2),
            "paid_total": round(total_paid, 2),
            "remaining_budget": round(budget - total_po, 2),
        }
