let currentSessionId = null;
let fullResponseText = "";
let currentMode = "file";

// --- Mode switching ---
function switchMode(mode) {
    currentMode = mode;
    document.getElementById("tabFile").classList.toggle("active", mode === "file");
    document.getElementById("tabManual").classList.toggle("active", mode === "manual");
    document.getElementById("fileForm").style.display = mode === "file" ? "block" : "none";
    document.getElementById("briefForm").style.display = mode === "manual" ? "block" : "none";
}

// --- File upload ---
function handleDrop(e) {
    e.preventDefault();
    e.target.closest(".upload-zone").classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
}

async function handleFile(file) {
    if (!file) return;

    const ext = file.name.split(".").pop().toLowerCase();
    if (!["docx", "txt"].includes(ext)) {
        alert("Поддерживаются только .docx и .txt файлы");
        return;
    }

    document.getElementById("fileName").textContent = file.name;

    if (ext === "txt") {
        const text = await file.text();
        showBriefPreview(text);
    } else {
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/upload-brief", { method: "POST", body: formData });
            const data = await res.json();
            if (data.error) {
                alert(data.error);
                return;
            }
            showBriefPreview(data.text);
        } catch (err) {
            alert("Ошибка загрузки файла: " + err.message);
        }
    }
}

function showBriefPreview(text) {
    document.getElementById("briefText").value = text;
    document.getElementById("uploadZone").style.display = "none";
    document.getElementById("filePreview").style.display = "block";
    document.getElementById("generateFromFileBtn").disabled = false;
}

function removeFile() {
    document.getElementById("fileInput").value = "";
    document.getElementById("briefText").value = "";
    document.getElementById("uploadZone").style.display = "block";
    document.getElementById("filePreview").style.display = "none";
    document.getElementById("generateFromFileBtn").disabled = true;
}

// --- Generate from file ---
async function generateFromFile() {
    const text = document.getElementById("briefText").value.trim();
    if (!text) {
        alert("Загрузите файл с ТЗ");
        return;
    }

    showResultArea();
    document.getElementById("generateFromFileBtn").disabled = true;

    try {
        const response = await fetch("/api/generate-from-brief", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        const data = await response.json();
        handleResponse(data);
    } catch (err) {
        document.getElementById("articleContent").innerHTML =
            `<p style="color:red">Ошибка: ${err.message}</p>`;
    }

    document.getElementById("generateFromFileBtn").disabled = false;
}

// --- Generate from manual form ---
async function generateArticle() {
    const topic = document.getElementById("topic").value.trim();
    const mainKeywords = document.getElementById("mainKeywords").value.trim();

    if (!topic || !mainKeywords) {
        alert("Заполните тему и ключевые слова");
        return;
    }

    const payload = {
        topic,
        h1: document.getElementById("h1").value.trim(),
        content_type: document.getElementById("contentType").value,
        main_keywords: mainKeywords,
        thematic_words: document.getElementById("thematicWords").value.trim(),
        highlight_words: document.getElementById("highlightWords").value.trim(),
        word_count: parseInt(document.getElementById("wordCount").value) || 3000,
        structure: document.getElementById("structure").value.trim(),
        aeo_questions: document.getElementById("aeoQuestions").value.trim(),
        meta_title: document.getElementById("metaTitleInput").value.trim(),
        meta_description: document.getElementById("metaDescInput").value.trim(),
        competitors: document.getElementById("competitors").value.trim(),
        additional: document.getElementById("additional").value.trim(),
    };

    showResultArea();
    document.getElementById("generateBtn").disabled = true;

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        handleResponse(data);
    } catch (err) {
        document.getElementById("articleContent").innerHTML =
            `<p style="color:red">Ошибка: ${err.message}</p>`;
    }

    document.getElementById("generateBtn").disabled = false;
}

function handleResponse(data) {
    if (data.error) {
        document.getElementById("articleContent").innerHTML =
            `<p style="color:red">Ошибка: ${data.error}</p>`;
        return;
    }

    fullResponseText = data.text;
    if (data.session_id) {
        currentSessionId = data.session_id;
    }
    renderArticle(fullResponseText);
    document.getElementById("chatSection").style.display = "block";
}

function showResultArea() {
    document.getElementById("fileForm").style.display = "none";
    document.getElementById("briefForm").style.display = "none";
    document.querySelector(".mode-tabs").style.display = "none";
    const resultArea = document.getElementById("resultArea");
    resultArea.classList.add("active");
    document.getElementById("articleContent").innerHTML =
        '<div class="loading">Генерирую статью</div>';
    document.getElementById("metaBlock").style.display = "none";
    document.getElementById("chatSection").style.display = "none";
}

// --- Chat for iterations ---
async function sendChat() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (!message || !currentSessionId) return;

    addChatMessage(message, "user");
    input.value = "";
    document.getElementById("sendBtn").disabled = true;

    document.getElementById("articleContent").innerHTML =
        '<div class="loading">Обновляю статью</div>';
    document.getElementById("metaBlock").style.display = "none";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, message }),
        });
        const data = await response.json();

        if (data.error) {
            document.getElementById("articleContent").innerHTML =
                `<p style="color:red">Ошибка: ${data.error}</p>`;
        } else {
            fullResponseText = data.text;
            renderArticle(fullResponseText);
        }
    } catch (err) {
        document.getElementById("articleContent").innerHTML =
            `<p style="color:red">Ошибка: ${err.message}</p>`;
    }

    document.getElementById("sendBtn").disabled = false;
}

// --- Rendering ---
function renderArticle(text) {
    const metaMatch = text.match(/---META---([\s\S]*?)---\/META---/);
    const articleMatch = text.match(/---ARTICLE---([\s\S]*?)---\/ARTICLE---/);

    if (metaMatch) {
        const metaText = metaMatch[1];
        const titleMatch = metaText.match(/Title:\s*(.+)/);
        const descMatch = metaText.match(/Description:\s*(.+)/);

        if (titleMatch) document.getElementById("metaTitle").textContent = titleMatch[1].trim();
        if (descMatch) document.getElementById("metaDesc").textContent = descMatch[1].trim();
        document.getElementById("metaBlock").style.display = "block";
    }

    let articleText = articleMatch ? articleMatch[1].trim() : text;

    if (!articleMatch) {
        articleText = text
            .replace(/---META---[\s\S]*?---\/META---/, "")
            .replace(/---ARTICLE---/, "")
            .replace(/---\/ARTICLE---/, "")
            .trim();
    }

    document.getElementById("articleContent").innerHTML = markdownToHtml(articleText);

    // Character counter (without spaces)
    const plainText = articleText.replace(/[#*\-\[\]()>|`]/g, "").trim();
    const charCount = plainText.replace(/\s/g, "").length;
    document.getElementById("charCount").textContent = charCount.toLocaleString("ru-RU");
    document.getElementById("charCounter").style.display = "block";
}

function markdownToHtml(md) {
    if (!md) return '<div class="loading">Генерирую статью</div>';

    let html = md
        .replace(/^### (.+)$/gm, "<h3>$1</h3>")
        .replace(/^## (.+)$/gm, "<h2>$1</h2>")
        .replace(/^# (.+)$/gm, "<h1>$1</h1>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/^- (.+)$/gm, "<li>$1</li>")
        .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
        .replace(/\n\n/g, "</p><p>")
        .replace(/\n/g, "<br>");

    html = html.replace(/(<li>.*?<\/li>(?:<br>)?)+/g, (match) => {
        return "<ul>" + match.replace(/<br>/g, "") + "</ul>";
    });

    return "<p>" + html + "</p>";
}

function addChatMessage(text, role) {
    const messages = document.getElementById("chatMessages");
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function copyArticle() {
    const metaMatch = fullResponseText.match(/---META---([\s\S]*?)---\/META---/);
    const articleMatch = fullResponseText.match(/---ARTICLE---([\s\S]*?)---\/ARTICLE---/);

    let copyText = "";
    if (metaMatch) copyText += metaMatch[1].trim() + "\n\n";
    if (articleMatch) copyText += articleMatch[1].trim();
    else copyText += fullResponseText;

    navigator.clipboard.writeText(copyText).then(() => {
        const btn = document.querySelector(".btn-copy");
        btn.textContent = "Скопировано!";
        setTimeout(() => (btn.textContent = "Копировать"), 2000);
    });
}

async function downloadDocx() {
    if (!fullResponseText) return;

    try {
        const response = await fetch("/api/export-docx", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: fullResponseText }),
        });

        if (!response.ok) {
            alert("Ошибка экспорта");
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "article.docx";
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert("Ошибка экспорта: " + err.message);
    }
}

function newArticle() {
    currentSessionId = null;
    fullResponseText = "";
    document.querySelector(".mode-tabs").style.display = "flex";
    document.getElementById("resultArea").classList.remove("active");
    document.getElementById("chatMessages").innerHTML = "";
    switchMode(currentMode);
}
