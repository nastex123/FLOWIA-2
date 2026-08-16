"use client";

import { useCallback, useEffect, useState } from "react";
import {
  KeyRound,
  Webhook,
  Workflow,
  Plus,
  Trash2,
  Copy,
  Check,
  Loader2,
  Send,
  FlaskConical,
  ShieldCheck,
} from "lucide-react";
import {
  createApiKey,
  createRule,
  createWebhook,
  deleteRule,
  deleteWebhook,
  evaluateRule,
  listApiKeys,
  listRules,
  listWebhooks,
  revokeApiKey,
  testWebhook,
} from "@/lib/api";
import { useAuthGuard } from "@/lib/useAuthGuard";
import type {
  ApiKeyItem,
  AutomationRule,
  RuleEvent,
  RuleOperator,
  WebhookConfig,
} from "@/types";

type Tab = "apikeys" | "webhooks" | "rules";

const OPERATORS: { value: RuleOperator; label: string }[] = [
  { value: "gt", label: "mayor que (>)" },
  { value: "gte", label: "mayor o igual (>=)" },
  { value: "lt", label: "menor que (<)" },
  { value: "lte", label: "menor o igual (<=)" },
  { value: "eq", label: "igual a (==)" },
  { value: "neq", label: "distinto de (!=)" },
  { value: "contains", label: "contiene" },
  { value: "is_empty", label: "está vacío" },
  { value: "not_empty", label: "no está vacío" },
];

const EVENTS: { value: RuleEvent; label: string }[] = [
  { value: "extraction_completed", label: "Al completar extracción" },
  { value: "normalization_completed", label: "Al completar normalización" },
];

function cn(...classes: (string | false | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

export default function SettingsPage() {
  useAuthGuard();
  const [tab, setTab] = useState<Tab>("apikeys");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Automatización & Seguridad</h1>
        <p className="text-sm text-slate-400 mt-1">
          API Keys para ingesta desatendida, webhooks salientes y reglas de automatización de negocio.
        </p>
      </div>

      <div className="flex items-center gap-2 border-b border-slate-800">
        {(
          [
            { id: "apikeys", label: "API Keys", icon: KeyRound },
            { id: "webhooks", label: "Webhooks", icon: Webhook },
            { id: "rules", label: "Reglas", icon: Workflow },
          ] as { id: Tab; label: string; icon: typeof KeyRound }[]
        ).map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors",
              tab === id
                ? "border-indigo-500 text-white"
                : "border-transparent text-slate-400 hover:text-slate-200"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {tab === "apikeys" && <ApiKeysPanel />}
      {tab === "webhooks" && <WebhooksPanel />}
      {tab === "rules" && <RulesPanel />}
    </div>
  );
}

// ==========================================
// API Keys Panel
// ==========================================

function ApiKeysPanel() {
  const [keys, setKeys] = useState<ApiKeyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKeys = useCallback(async () => {
    try {
      setKeys(await listApiKeys());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando API Keys");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setCreatedKey(null);
    try {
      const created = await createApiKey(name);
      setCreatedKey(created.key);
      setName("");
      await fetchKeys();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error creando API Key");
    } finally {
      setBusy(false);
    }
  };

  const copyKey = async () => {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-white mb-1">Nueva API Key</h2>
        <p className="text-xs text-slate-500 mb-4">
          Para integraciones desatendidas (cURL, scripts, ERPs). La clave solo se muestra una vez.
        </p>
        <form onSubmit={handleCreate} className="flex items-center gap-3">
          <input
            type="text"
            required
            minLength={2}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej. Integración ERP Contabilidad"
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={busy}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors"
          >
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Generar
          </button>
        </form>
      </div>

      {createdKey && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-emerald-300 font-medium">
              API Key generada. Cópiala ahora; no volverá a mostrarse:
            </p>
            <button
              onClick={copyKey}
              className="flex items-center gap-1.5 text-xs text-emerald-300 hover:text-emerald-200"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copiada" : "Copiar"}
            </button>
          </div>
          <code className="block mt-2 text-sm font-mono text-white bg-slate-950/60 rounded-lg px-3 py-2 break-all">
            {createdKey}
          </code>
        </div>
      )}

      {error && (
        <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500 font-medium">
          Claves activas ({keys.length})
        </div>
        {loading ? (
          <div className="p-6 text-sm text-slate-500">Cargando...</div>
        ) : keys.length === 0 ? (
          <div className="p-6 text-sm text-slate-500">Aún no hay API Keys.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-slate-500 uppercase">
              <tr>
                <th className="px-5 py-3 font-medium">Nombre</th>
                <th className="px-5 py-3 font-medium">Prefijo</th>
                <th className="px-5 py-3 font-medium">Estado</th>
                <th className="px-5 py-3 font-medium">Último uso</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {keys.map((k) => (
                <tr key={k.id}>
                  <td className="px-5 py-3 text-slate-200">{k.name}</td>
                  <td className="px-5 py-3 font-mono text-xs text-slate-400">{k.prefix}…</td>
                  <td className="px-5 py-3">
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded-full text-[11px]",
                        k.is_active
                          ? "bg-emerald-500/10 text-emerald-400"
                          : "bg-rose-500/10 text-rose-400"
                      )}
                    >
                      {k.is_active ? "Activa" : "Revocada"}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-xs text-slate-400">
                    {k.last_used_at ? new Date(k.last_used_at).toLocaleString() : "Nunca"}
                  </td>
                  <td className="px-5 py-3 text-right">
                    {k.is_active && (
                      <button
                        onClick={async () => {
                          await revokeApiKey(k.id);
                          fetchKeys();
                        }}
                        title="Revocar"
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800/60"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// ==========================================
// Webhooks Panel
// ==========================================

function WebhooksPanel() {
  const [webhooks, setWebhooks] = useState<WebhookConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    name: "",
    url: "",
    secret: "",
    headers: "",
  });
  const [busy, setBusy] = useState(false);
  const [testResult, setTestResult] = useState<Record<string, { status: string; http_status?: number | null }>>({});
  const [error, setError] = useState<string | null>(null);

  const fetchWebhooks = useCallback(async () => {
    try {
      setWebhooks(await listWebhooks());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando webhooks");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWebhooks();
  }, [fetchWebhooks]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const headers: Record<string, string> = {};
      form.headers.split("\n").forEach((line) => {
        const idx = line.indexOf(":");
        if (idx > 0) headers[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
      });
      await createWebhook({
        name: form.name,
        url: form.url,
        secret: form.secret || null,
        headers,
      });
      setForm({ name: "", url: "", secret: "", headers: "" });
      await fetchWebhooks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error creando webhook");
    } finally {
      setBusy(false);
    }
  };

  const handleTest = async (id: string) => {
    try {
      const result = await testWebhook(id);
      setTestResult((prev) => ({ ...prev, [id]: result }));
    } catch (err) {
      setTestResult((prev) => ({
        ...prev,
        [id]: { status: "error" },
      }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-white mb-1">Nuevo Webhook Saliente</h2>
        <p className="text-xs text-slate-500 mb-4">
          Endpoint destino (ERP, Zapier, Make, n8n...) que se invocará al completar extracción o normalización.
        </p>
        <form onSubmit={handleCreate} className="space-y-3">
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Nombre (ej. ERP Contabilidad)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              type="url"
              required
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="https://erp.example.com/webhook"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              type="password"
              value={form.secret}
              onChange={(e) => setForm({ ...form, secret: e.target.value })}
              placeholder="Secreto HMAC (opcional)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <textarea
              value={form.headers}
              onChange={(e) => setForm({ ...form, headers: e.target.value })}
              placeholder={"Cabeceras extra (Clave: Valor, una por línea)"}
              rows={1}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors"
          >
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Registrar Webhook
          </button>
        </form>
      </div>

      {error && (
        <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {loading ? (
          <div className="p-6 text-sm text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">Cargando...</div>
        ) : webhooks.length === 0 ? (
          <div className="p-6 text-sm text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">
            No hay webhooks configurados.
          </div>
        ) : (
          webhooks.map((w) => {
            const test = testResult[w.id];
            return (
              <div key={w.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-white">{w.name}</h3>
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded-full text-[11px]",
                          w.active
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-slate-800 text-slate-500"
                        )}
                      >
                        {w.active ? "Activo" : "Inactivo"}
                      </span>
                      {w.has_secret && (
                        <span className="flex items-center gap-1 text-[11px] text-indigo-400">
                          <ShieldCheck className="w-3 h-3" /> Firmado HMAC
                        </span>
                      )}
                    </div>
                    <code className="text-xs text-slate-500 break-all">{w.url}</code>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleTest(w.id)}
                      className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
                    >
                      <Send className="w-3.5 h-3.5" />
                      Test
                    </button>
                    <button
                      onClick={async () => {
                        await deleteWebhook(w.id);
                        fetchWebhooks();
                      }}
                      title="Eliminar"
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800/60"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {test && (
                  <div
                    className={cn(
                      "mt-3 text-xs rounded-lg px-3 py-2",
                      test.status === "success"
                        ? "bg-emerald-500/10 text-emerald-300"
                        : "bg-rose-500/10 text-rose-300"
                    )}
                  >
                    Test: {test.status === "success" ? "Entregado" : "Falló"}
                    {test.http_status != null && ` · HTTP ${test.http_status}`}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

// ==========================================
// Rules Panel
// ==========================================

function RulesPanel() {
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    name: "",
    document_type: "",
    event: "extraction_completed" as RuleEvent,
    field: "total_amount",
    operator: "gt" as RuleOperator,
    value: "",
    webhook_ids: [] as string[],
    enabled: true,
  });
  const [evalState, setEvalState] = useState<Record<string, { docId: string; result?: boolean }>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    try {
      const [r, w] = await Promise.all([listRules(), listWebhooks()]);
      setRules(r);
      setWebhooks(w);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando reglas");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const value =
        form.operator === "is_empty" || form.operator === "not_empty"
          ? null
          : form.value;
      await createRule({
        name: form.name,
        document_type: form.document_type || null,
        event: form.event,
        field: form.field,
        operator: form.operator,
        value,
        webhook_ids: form.webhook_ids,
        enabled: form.enabled,
      });
      setForm((f) => ({ ...f, name: "", value: "" }));
      await fetchAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error creando regla");
    } finally {
      setBusy(false);
    }
  };

  const handleEvaluate = async (ruleId: string) => {
    const docId = evalState[ruleId]?.docId;
    if (!docId) return;
    try {
      const result = await evaluateRule(ruleId, docId);
      setEvalState((prev) => ({ ...prev, [ruleId]: { docId, result: result.matched } }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error evaluando regla");
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-white mb-1">Nueva Regla de Negocio</h2>
        <p className="text-xs text-slate-500 mb-4">
          Ej: "Alertar si total &gt; 5.000€" o "Validar obligatoriedad de CIF".
        </p>
        <form onSubmit={handleCreate} className="space-y-3">
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              type="text"
              required
              minLength={2}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Nombre de la regla (ej. Alertar si total > 5000)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              type="text"
              value={form.document_type}
              onChange={(e) => setForm({ ...form, document_type: e.target.value })}
              placeholder="Tipo documento (vacío = todos, ej. invoice)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="grid sm:grid-cols-3 gap-3">
            <select
              value={form.event}
              onChange={(e) => setForm({ ...form, event: e.target.value as RuleEvent })}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {EVENTS.map((ev) => (
                <option key={ev.value} value={ev.value}>
                  {ev.label}
                </option>
              ))}
            </select>
            <input
              type="text"
              required
              value={form.field}
              onChange={(e) => setForm({ ...form, field: e.target.value })}
              placeholder="Campo (ej. total_amount, tax_id)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <select
              value={form.operator}
              onChange={(e) => setForm({ ...form, operator: e.target.value as RuleOperator })}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {OPERATORS.map((op) => (
                <option key={op.value} value={op.value}>
                  {op.label}
                </option>
              ))}
            </select>
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              type="text"
              value={form.value}
              onChange={(e) => setForm({ ...form, value: e.target.value })}
              disabled={form.operator === "is_empty" || form.operator === "not_empty"}
              placeholder="Valor umbral (ej. 5000)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
            />
            <select
              value={form.webhook_ids[0] || ""}
              onChange={(e) =>
                setForm({ ...form, webhook_ids: e.target.value ? [e.target.value] : [] })
              }
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Webhook destino (todos si vacío)</option>
              {webhooks.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={form.enabled}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500"
            />
            Regla habilitada
          </label>
          <button
            type="submit"
            disabled={busy}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors"
          >
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Crear Regla
          </button>
        </form>
      </div>

      {error && (
        <div className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {loading ? (
          <div className="p-6 text-sm text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">Cargando...</div>
        ) : rules.length === 0 ? (
          <div className="p-6 text-sm text-slate-500 bg-slate-900 border border-slate-800 rounded-2xl">
            No hay reglas de automatización configuradas.
          </div>
        ) : (
          rules.map((r) => {
            const ev = evalState[r.id];
            return (
              <div key={r.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-white">{r.name}</h3>
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded-full text-[11px]",
                          r.enabled
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-slate-800 text-slate-500"
                        )}
                      >
                        {r.enabled ? "Activa" : "Inactiva"}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {r.event === "extraction_completed" ? "Extracción" : "Normalización"} ·{" "}
                      <code className="text-indigo-300">{r.field}</code> {r.operator}
                      {r.value !== null && r.value !== undefined && r.value !== "" && (
                        <> <code className="text-slate-300">{String(r.value)}</code></>
                      )}
                      {r.document_type && (
                        <span className="ml-2 text-slate-500">({r.document_type})</span>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={ev?.docId || ""}
                        onChange={(e) =>
                          setEvalState((prev) => ({ ...prev, [r.id]: { docId: e.target.value, result: prev[r.id]?.result } }))
                        }
                        placeholder="ID documento (test)"
                        className="w-44 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                      <button
                        onClick={() => handleEvaluate(r.id)}
                        disabled={!ev?.docId}
                        title="Evaluar regla (dry-run)"
                        className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 transition-colors"
                      >
                        <FlaskConical className="w-3.5 h-3.5" />
                        Evaluar
                      </button>
                    </div>
                    <button
                      onClick={async () => {
                        await deleteRule(r.id);
                        fetchAll();
                      }}
                      title="Eliminar"
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800/60"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {ev?.result !== undefined && (
                  <div
                    className={cn(
                      "mt-3 text-xs rounded-lg px-3 py-2",
                      ev.result
                        ? "bg-emerald-500/10 text-emerald-300"
                        : "bg-slate-800/60 text-slate-400"
                    )}
                  >
                    Evaluación: {ev.result ? "Coincide (se dispararía el webhook)" : "No coincide"}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}