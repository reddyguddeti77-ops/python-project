let currentResults = [];

async function fetchResults() {
  const res = await fetch("/api/results");
  const data = await res.json();
  currentResults = data.rows || [];
  renderSummary(currentResults);
  renderTable(currentResults);
}

function renderSummary(results) {
  const counts = {};
  results.forEach((r) => { counts[r.status] = (counts[r.status] || 0) + 1; });

  const container = document.getElementById("summary-cards");
  container.innerHTML = "";

  if (Object.keys(counts).length === 0) {
    container.innerHTML = '<p class="empty-msg">No results yet. Upload files above to get started.</p>';
  } else {
    Object.entries(counts).forEach(([status, count]) => {
      const box = document.createElement("div");
      box.className = `summary-box status-${status}`;
      box.innerHTML = `<span class="count">${count}</span><span class="label">${status}</span>`;
      container.appendChild(box);
    });
  }

  const filter = document.getElementById("status-filter");
  const current = filter.value;
  filter.innerHTML = '<option value="ALL">All</option>';
  Object.keys(counts).forEach((status) => {
    const opt = document.createElement("option");
    opt.value = status;
    opt.textContent = status;
    filter.appendChild(opt);
  });
  filter.value = Object.keys(counts).includes(current) ? current : "ALL";
}

function renderTable(results) {
  const filterValue = document.getElementById("status-filter").value;
  const rows = filterValue === "ALL" ? results : results.filter((r) => r.status === filterValue);

  const body = document.getElementById("results-body");
  body.innerHTML = "";

  if (rows.length === 0) {
    body.innerHTML = '<tr><td colspan="6" class="empty-msg">No transactions to show.</td></tr>';
    return;
  }

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.txn_id}</td>
      <td>${r.matched_rrn || "-"}</td>
      <td>${Number(r.merchant_amount).toFixed(2)}</td>
      <td>${r.settled_amount !== null && r.settled_amount !== undefined ? Number(r.settled_amount).toFixed(2) : "-"}</td>
      <td class="status-cell"><span class="status-${r.status}">${r.status}</span></td>
      <td>${r.notes}</td>
    `;
    body.appendChild(tr);
  });
}

document.getElementById("status-filter").addEventListener("change", () => renderTable(currentResults));

document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const statusEl = document.getElementById("upload-status");
  statusEl.classList.remove("error");
  statusEl.textContent = "Uploading and running reconciliation...";

  const merchantFile = document.getElementById("merchant-file").files[0];
  const settlementFile = document.getElementById("settlement-file").files[0];

  if (!merchantFile || !settlementFile) {
    statusEl.classList.add("error");
    statusEl.textContent = "Please choose both files.";
    return;
  }

  const formData = new FormData();
  formData.append("merchant_file", merchantFile);
  formData.append("settlement_file", settlementFile);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Upload failed.");
    statusEl.textContent = "Done! Results updated below.";
    await fetchResults();
  } catch (err) {
    statusEl.classList.add("error");
    statusEl.textContent = "Error: " + err.message;
    console.error(err);
  }
});

document.getElementById("download-btn").addEventListener("click", () => {
  if (currentResults.length === 0) return;
  const headers = ["txn_id", "matched_rrn", "merchant_amount", "settled_amount", "status", "notes"];
  const csvLines = [headers.join(",")];
  currentResults.forEach((r) => {
    csvLines.push(headers.map((h) => `"${r[h] ?? ""}"`).join(","));
  });
  const blob = new Blob([csvLines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "reconciliation_report.csv";
  a.click();
  URL.revokeObjectURL(url);
});

fetchResults();
